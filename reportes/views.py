from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, MovimientoInventario
from clientes.models import Pedido
from usuarios.models import Usuario
from core.permissions import rol_requerido, RolRequeridoMixin
from django.views.generic import TemplateView

@login_required
@rol_requerido(['gerente', 'admin', 'vendedor'])
def dashboard_view(request):
    """Dashboard principal de reportes"""
    hoy = timezone.now().date()
    hace_un_mes = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)

    # --- Métricas Principales ---
    ventas_mes = Venta.objects.filter(fecha_venta__date__gte=hace_un_mes).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    nuevos_clientes = Usuario.objects.filter(
        rol='cliente',
        date_joined__date__gte=hace_un_mes
    ).count()

    productos_bajo_stock = Producto.objects.filter(stock__lte=F('stock_minimo')).count()

    # --- Datos para el Gráfico de Ventas (últimos 7 días) ---
    ventas_diarias = Venta.objects.filter(
        fecha_venta__date__gte=hace_7_dias
    ).values('fecha_venta__date').annotate(
        total_dia=Sum('total')
    ).order_by('fecha_venta__date')

    # Formatear para el gráfico
    labels_grafico = [v['fecha_venta__date'].strftime('%d-%m') for v in ventas_diarias]
    data_grafico = [float(v['total_dia']) for v in ventas_diarias]

    # --- Actividad Reciente ---
    ultimas_ventas = Venta.objects.select_related('cliente').order_by('-fecha_venta')[:3]
    ultimos_usuarios = Usuario.objects.filter(rol='cliente').order_by('-date_joined')[:2]

    context = {
        'ventas_mes': ventas_mes,
        'nuevos_clientes': nuevos_clientes,
        'productos_bajo_stock': productos_bajo_stock,
        'labels_grafico': labels_grafico,
        'data_grafico': data_grafico,
        'ultimas_ventas': ultimas_ventas,
        'ultimos_usuarios': ultimos_usuarios,
    }
    
    return render(request, 'reportes/dashboard.html', context)

@login_required
@rol_requerido(['gerente', 'admin'])
def reporte_ventas(request):
    """Reporte detallado de ventas"""
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    ventas = Venta.objects.filter(estado='completada')
    
    if fecha_desde:
        try:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)
        except ValueError:
            pass
    
    # Estadísticas del período
    total_ventas = ventas.count()
    total_ingresos = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio_venta = total_ingresos / total_ventas if total_ventas > 0 else 0
    
    context = {
        'ventas': ventas.order_by('-fecha_venta')[:50],  # Últimas 50
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'promedio_venta': promedio_venta,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'reportes/ventas.html', context)

@login_required
@rol_requerido(['gerente', 'admin'])
def reporte_inventario(request):
    """Reporte de inventario"""
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    
    # Filtros
    bajo_stock = request.GET.get('bajo_stock')
    if bajo_stock:
        productos = productos.filter(stock__lte=F('stock_minimo'))
    
    # Estadísticas
    total_productos = productos.count()
    productos_bajo_stock = Producto.objects.filter(
        activo=True,
        stock__lte=F('stock_minimo')
    ).count()
    valor_total_inventario = productos.aggregate(
        total=Sum(F('stock') * F('precio'))
    )['total'] or 0
    
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'valor_total_inventario': valor_total_inventario,
    }
    
    return render(request, 'reportes/inventario.html', context)

class ReporteVentasView(RolRequeridoMixin, TemplateView):
    template_name = 'reportes/ventas.html'
    roles_permitidos = ['gerente', 'admin']

class ReporteInventarioView(RolRequeridoMixin, TemplateView):
    template_name = 'reportes/inventario.html'
    roles_permitidos = ['gerente', 'admin']

class ReporteClientesView(RolRequeridoMixin, TemplateView):
    template_name = 'reportes/clientes.html'
    roles_permitidos = ['gerente', 'admin']

class ReporteFinancieroView(RolRequeridoMixin, TemplateView):
    template_name = 'reportes/financiero.html'
    roles_permitidos = ['gerente', 'admin']
