from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from .models import Venta, DetalleVenta, Factura
from .forms import VentaForm
from .serializers import VentaSerializer
from core.permissions import RolRequeridoMixin
from inventario.models import Producto, MovimientoInventario

class VentasListView(RolRequeridoMixin, ListView):
    model = Venta
    template_name = 'ventas/ventas_list.html'
    context_object_name = 'ventas'
    roles_permitidos = ['vendedor', 'gerente', 'admin']
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Venta.objects.select_related('vendedor', 'cliente').order_by('-fecha_venta')
        
        # Filtros
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__date__lte=fecha_hasta)
        
        vendedor_id = self.request.GET.get('vendedor')
        if vendedor_id:
            queryset = queryset.filter(vendedor_id=vendedor_id)
        
        return queryset

class RegistrarVentaView(RolRequeridoMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/registrar_venta.html'
    success_url = reverse_lazy('ventas:lista')
    roles_permitidos = ['vendedor', 'gerente', 'admin']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.filter(activo=True, stock__gt=0)
        return context
    
    def form_valid(self, form):
        venta = form.save(commit=False)
        venta.vendedor = self.request.user
        venta.numero_venta = f"VTA-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        venta.tipo = 'presencial'
        
        # Procesar items del carrito (desde JavaScript)
        items_data = self.request.POST.get('items_data')
        if not items_data:
            messages.error(self.request, 'Debe agregar al menos un producto a la venta.')
            return super().form_invalid(form)
        
        import json
        items = json.loads(items_data)
        
        # Calcular totales
        subtotal = 0
        for item in items:
            producto = Producto.objects.get(id=item['producto_id'])
            cantidad = int(item['cantidad'])
            precio = float(item['precio'])
            subtotal += cantidad * precio
        
        venta.subtotal = subtotal
        venta.impuesto = subtotal * 0.19  # IVA 19%
        venta.total = venta.subtotal + venta.impuesto - venta.descuento
        venta.save()
        
        # Crear detalles de venta
        for item in items:
            producto = Producto.objects.get(id=item['producto_id'])
            cantidad = int(item['cantidad'])
            precio = float(item['precio'])
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=cantidad * precio
            )
            
            # Actualizar stock
            producto.stock -= cantidad
            producto.save()
            
            # Registrar movimiento
            MovimientoInventario.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=cantidad,
                motivo=f'Venta {venta.numero_venta}',
                usuario=self.request.user
            )
        
        messages.success(self.request, f'Venta {venta.numero_venta} registrada exitosamente.')
        return redirect('ventas:detalle', pk=venta.pk)

class VentaDetailView(RolRequeridoMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detalle.html'
    context_object_name = 'venta'
    roles_permitidos = ['vendedor', 'gerente', 'admin', 'cliente']
    
    def get_object(self):
        venta = super().get_object()
        # Los clientes solo pueden ver sus propias ventas
        if self.request.user.rol == 'cliente' and venta.cliente != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()
        return venta

def generar_factura_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Verificar permisos
    if request.user.rol == 'cliente' and venta.cliente != request.user:
        messages.error(request, 'No tienes permisos para ver esta factura.')
        return redirect('home')
    
    # Crear factura si no existe
    factura, created = Factura.objects.get_or_create(
        venta=venta,
        defaults={
            'numero_factura': f"FAC-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            'tipo': 'factura',
            'cliente_nombre': venta.cliente.get_full_name() if venta.cliente else 'Cliente General',
            'cliente_rut': venta.cliente.rut if venta.cliente else '',
            'cliente_direccion': venta.cliente.direccion if venta.cliente else ''
        }
    )
    
    # Generar PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Encabezado
    story.append(Paragraph("PERFULANDIA SPA", styles['Title']))
    story.append(Paragraph("RUT: 12.345.678-9", styles['Normal']))
    story.append(Paragraph("Dirección: Av. Principal 1234, Santiago", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Información de la factura
    story.append(Paragraph(f"FACTURA N° {factura.numero_factura}", styles['Heading1']))
    story.append(Paragraph(f"Fecha: {factura.fecha_emision.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Información del cliente
    story.append(Paragraph("DATOS DEL CLIENTE:", styles['Heading2']))
    story.append(Paragraph(f"Nombre: {factura.cliente_nombre}", styles['Normal']))
    if factura.cliente_rut:
        story.append(Paragraph(f"RUT: {factura.cliente_rut}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Tabla de productos
    data = [['Código', 'Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
    for detalle in venta.detalles.all():
        data.append([
            detalle.producto.codigo,
            detalle.producto.nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario:,.0f}",
            f"${detalle.subtotal:,.0f}"
        ])
    
    # Totales
    data.append(['', '', '', 'Subtotal:', f"${venta.subtotal:,.0f}"])
    data.append(['', '', '', 'IVA (19%):', f"${venta.impuesto:,.0f}"])
    if venta.descuento > 0:
        data.append(['', '', '', 'Descuento:', f"-${venta.descuento:,.0f}"])
    data.append(['', '', '', 'TOTAL:', f"${venta.total:,.0f}"])
    
    table = Table(data, colWidths=[1*inch, 3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    # Respuesta HTTP
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{factura.numero_factura}.pdf"'
    
    return response

# API ViewSet
class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        hoy = timezone.now().date()
        
        stats = {
            'ventas_hoy': self.queryset.filter(fecha_venta__date=hoy).count(),
            'ingresos_hoy': self.queryset.filter(
                fecha_venta__date=hoy,
                estado='completada'
            ).aggregate(total=Sum('total'))['total'] or 0,
            'productos_vendidos_hoy': DetalleVenta.objects.filter(
                venta__fecha_venta__date=hoy
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        }
        
        return Response(stats)