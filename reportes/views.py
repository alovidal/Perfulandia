from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, Avg
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
    ventas_mes = Venta.objects.filter(
        fecha_venta__date__gte=hace_un_mes,
        estado='completada'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    ventas_hoy = Venta.objects.filter(
        fecha_venta__date=hoy,
        estado='completada'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    nuevos_clientes = Usuario.objects.filter(
        rol='cliente',
        date_joined__date__gte=hace_un_mes
    ).count()

    productos_bajo_stock = Producto.objects.filter(
        stock__lte=F('stock_minimo'),
        activo=True
    ).count()

    # --- Datos para el Gráfico de Ventas (últimos 7 días) ---
    ventas_diarias = []
    for i in range(7):
        fecha = hoy - timedelta(days=6-i)
        total_dia = Venta.objects.filter(
            fecha_venta__date=fecha,
            estado='completada'
        ).aggregate(total=Sum('total'))['total'] or 0
        ventas_diarias.append({
            'fecha': fecha,
            'total': float(total_dia)
        })

    # Formatear para el gráfico
    labels_grafico = [v['fecha'].strftime('%d-%m') for v in ventas_diarias]
    data_grafico = [v['total'] for v in ventas_diarias]

    # --- Productos más vendidos (últimos 30 días) ---
    productos_top = DetalleVenta.objects.filter(
        venta__fecha_venta__date__gte=hace_un_mes,
        venta__estado='completada'
    ).values(
        'producto__nombre',
        'producto__id'
    ).annotate(
        cantidad_vendida=Sum('cantidad'),
        ingresos=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-cantidad_vendida')[:5]

    # --- Actividad Reciente ---
    ultimas_ventas = Venta.objects.select_related('cliente').filter(
        estado='completada'
    ).order_by('-fecha_venta')[:5]
    
    ultimos_usuarios = Usuario.objects.filter(
        rol='cliente'
    ).order_by('-date_joined')[:3]

    # --- Métricas adicionales ---
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    ticket_promedio = ventas_mes / max(Venta.objects.filter(
        fecha_venta__date__gte=hace_un_mes,
        estado='completada'
    ).count(), 1)

    context = {
        'ventas_mes': ventas_mes,
        'ventas_hoy': ventas_hoy,
        'nuevos_clientes': nuevos_clientes,
        'productos_bajo_stock': productos_bajo_stock,
        'pedidos_pendientes': pedidos_pendientes,
        'ticket_promedio': ticket_promedio,
        'labels_grafico': labels_grafico,
        'data_grafico': data_grafico,
        'productos_top': productos_top,
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
    vendedor_id = request.GET.get('vendedor')
    
    ventas = Venta.objects.filter(estado='completada').select_related('cliente', 'vendedor')
    
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
    
    if vendedor_id:
        ventas = ventas.filter(vendedor_id=vendedor_id)
    
    # Estadísticas del período
    total_ventas = ventas.count()
    total_ingresos = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio_venta = total_ingresos / total_ventas if total_ventas > 0 else 0
    
    # Ventas por vendedor
    ventas_por_vendedor = ventas.values(
        'vendedor__username',
        'vendedor__first_name',
        'vendedor__last_name'
    ).annotate(
        total_ventas=Count('id'),
        total_ingresos=Sum('total')
    ).order_by('-total_ingresos')
    
    # Productos más vendidos en el período
    productos_periodo = DetalleVenta.objects.filter(
        venta__in=ventas
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingresos_total=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-ingresos_total')[:10]
    
    context = {
        'ventas': ventas.order_by('-fecha_venta')[:100],  # Últimas 100
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'promedio_venta': promedio_venta,
        'ventas_por_vendedor': ventas_por_vendedor,
        'productos_periodo': productos_periodo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'vendedores': Usuario.objects.filter(rol__in=['vendedor', 'gerente', 'admin']),
    }
    
    return render(request, 'reportes/ventas.html', context)

@login_required
@rol_requerido(['gerente', 'admin'])
def reporte_inventario(request):
    """Reporte de inventario"""
    categoria_id = request.GET.get('categoria')
    bajo_stock = request.GET.get('bajo_stock')
    orden = request.GET.get('orden', 'nombre')
    
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    
    # Filtros
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if bajo_stock:
        productos = productos.filter(stock__lte=F('stock_minimo'))
    
    # Ordenamiento
    if orden == 'stock_asc':
        productos = productos.order_by('stock')
    elif orden == 'stock_desc':
        productos = productos.order_by('-stock')
    elif orden == 'valor_desc':
        productos = productos.annotate(
            valor_inventario=F('stock') * F('precio')
        ).order_by('-valor_inventario')
    else:
        productos = productos.order_by('nombre')
    
    # Estadísticas
    total_productos = productos.count()
    productos_bajo_stock = productos.filter(stock__lte=F('stock_minimo')).count()
    productos_agotados = productos.filter(stock=0).count()
    
    valor_total_inventario = productos.aggregate(
        total=Sum(F('stock') * F('precio'))
    )['total'] or 0
    
    # Productos por categoría
    productos_por_categoria = productos.values(
        'categoria__nombre'
    ).annotate(
        cantidad=Count('id'),
        valor_total=Sum(F('stock') * F('precio'))
    ).order_by('-valor_total')
    
    # Movimientos recientes
    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto', 'usuario'
    ).order_by('-fecha')[:20]
    
    from inventario.models import Categoria
    context = {
        'productos': productos[:200],  # Limitar para performance
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_agotados': productos_agotados,
        'valor_total_inventario': valor_total_inventario,
        'productos_por_categoria': productos_por_categoria,
        'movimientos_recientes': movimientos_recientes,
        'categorias': Categoria.objects.filter(activa=True),
        'filtros': {
            'categoria_id': categoria_id,
            'bajo_stock': bajo_stock,
            'orden': orden,
        }
    }
    
    return render(request, 'reportes/inventario.html', context)

@login_required
@rol_requerido(['gerente', 'admin'])
def reporte_clientes(request):
    """Reporte de clientes"""
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    
    # Filtros de fecha para nuevos clientes
    clientes = Usuario.objects.filter(rol='cliente')
    if desde:
        try:
            desde = datetime.strptime(desde, '%Y-%m-%d').date()
            clientes = clientes.filter(date_joined__date__gte=desde)
        except ValueError:
            pass
    
    if hasta:
        try:
            hasta = datetime.strptime(hasta, '%Y-%m-%d').date()
            clientes = clientes.filter(date_joined__date__lte=hasta)
        except ValueError:
            pass
    
    # Estadísticas generales
    total_clientes = Usuario.objects.filter(rol='cliente').count()
    clientes_activos = Usuario.objects.filter(
        rol='cliente',
        ventas_cliente__isnull=False
    ).distinct().count()
    
    # Clientes con más compras
    mejores_clientes = Usuario.objects.filter(
        rol='cliente'
    ).annotate(
        total_compras=Count('ventas_cliente', filter=Q(ventas_cliente__estado='completada')),
        total_gastado=Sum('ventas_cliente__total', filter=Q(ventas_cliente__estado='completada'))
    ).filter(total_compras__gt=0).order_by('-total_gastado')[:10]
    
    # Clientes nuevos por mes
    hoy = timezone.now().date()
    clientes_por_mes = []
    for i in range(6):
        fecha_inicio = hoy.replace(day=1) - timedelta(days=30*i)
        fecha_fin = (fecha_inicio + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        count = Usuario.objects.filter(
            rol='cliente',
            date_joined__date__gte=fecha_inicio,
            date_joined__date__lte=fecha_fin
        ).count()
        
        clientes_por_mes.append({
            'mes': fecha_inicio.strftime('%B %Y'),
            'cantidad': count
        })
    
    clientes_por_mes.reverse()
    
    context = {
        'clientes': clientes.order_by('-date_joined')[:50],
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'mejores_clientes': mejores_clientes,
        'clientes_por_mes': clientes_por_mes,
        'nuevos_mes_actual': Usuario.objects.filter(
            rol='cliente',
            date_joined__date__gte=hoy.replace(day=1)
        ).count(),
    }
    
    return render(request, 'reportes/clientes.html', context)

@login_required
@rol_requerido(['gerente', 'admin'])
def reporte_financiero(request):
    """Reporte financiero"""
    año = request.GET.get('año', timezone.now().year)
    mes = request.GET.get('mes')
    
    # Filtros base
    ventas = Venta.objects.filter(
        estado='completada',
        fecha_venta__year=año
    )
    
    if mes:
        ventas = ventas.filter(fecha_venta__month=mes)
    
    # Ingresos por mes del año
    ingresos_mensuales = []
    for i in range(1, 13):
        total_mes = Venta.objects.filter(
            estado='completada',
            fecha_venta__year=año,
            fecha_venta__month=i
        ).aggregate(total=Sum('total'))['total'] or 0
        
        ingresos_mensuales.append({
            'mes': i,
            'nombre_mes': datetime(int(año), i, 1).strftime('%B'),
            'total': float(total_mes)
        })
    
    # Métricas principales
    total_ingresos = sum(mes['total'] for mes in ingresos_mensuales)
    promedio_mensual = total_ingresos / 12
    mejor_mes = max(ingresos_mensuales, key=lambda x: x['total'])
    
    # Análisis de crecimiento
    if len(ingresos_mensuales) >= 2:
        mes_anterior = ingresos_mensuales[-2]['total']
        mes_actual = ingresos_mensuales[-1]['total']
        crecimiento = ((mes_actual - mes_anterior) / max(mes_anterior, 1)) * 100
    else:
        crecimiento = 0
    
    # Costos estimados (productos vendidos * costo estimado)
    costos_estimados = DetalleVenta.objects.filter(
        venta__in=ventas
    ).aggregate(
        total=Sum(F('cantidad') * F('precio_unitario') * 0.6)  # Asumiendo 60% de costo
    )['total'] or 0
    
    ganancia_bruta = total_ingresos - costos_estimados
    margen_ganancia = (ganancia_bruta / max(total_ingresos, 1)) * 100
    
    context = {
        'año': año,
        'mes': mes,
        'ingresos_mensuales': ingresos_mensuales,
        'total_ingresos': total_ingresos,
        'promedio_mensual': promedio_mensual,
        'mejor_mes': mejor_mes,
        'crecimiento': crecimiento,
        'costos_estimados': costos_estimados,
        'ganancia_bruta': ganancia_bruta,
        'margen_ganancia': margen_ganancia,
        'años_disponibles': range(2020, timezone.now().year + 1),
    }
    
    return render(request, 'reportes/financiero.html', context)

# API para datos dinámicos
@login_required
def api_dashboard_data(request):
    """API para datos del dashboard en tiempo real"""
    if request.user.rol not in ['gerente', 'admin', 'vendedor']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(
        fecha_venta__date=hoy,
        estado='completada'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    return JsonResponse({
        'ventas_hoy': float(ventas_hoy),
        'timestamp': timezone.now().isoformat()
    })

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