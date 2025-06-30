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
from core.permissions import rol_requerido

@login_required
@rol_requerido(['gerente', 'admin'])
def dashboard_view(request):
    """Dashboard principal de reportes"""
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Estadísticas generales
    stats = {
        'ventas_hoy': Venta.objects.filter(fecha_venta__date=hoy).count(),
        'ventas_mes': Venta.objects.filter(fecha_venta__date__gte=hace_30_dias).count(),
        'ingresos_hoy': Venta.objects.filter(
            fecha_venta__date=hoy,
            estado='completada'
        ).aggregate(total=Sum('total'))['total'] or 0,
        'ingresos_mes': Venta.objects.filter(
            fecha_venta__date__gte=hace_30_dias,
            estado='completada'
        ).aggregate(total=Sum('total'))['total'] or 0,
        'productos_bajo_stock': Producto.objects.filter(
            stock__lte=F('stock_minimo')
        ).count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
        'total_clientes': Usuario.objects.filter(rol='cliente').count(),
    }
    
    # Productos más vendidos (últimos 30 días)
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha_venta__date__gte=hace_30_dias
    ).values(
        'producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'stats': stats,
        'productos_vendidos': productos_vendidos,
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
