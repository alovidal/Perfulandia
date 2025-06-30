from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Para todos los usuarios (autenticados o no)
        try:
            from inventario.models import Producto
            context['productos_destacados'] = Producto.objects.filter(activo=True, stock__gt=0).order_by('-fecha_creacion')[:8]
        except (ImportError, Exception):
            context['productos_destacados'] = []

        if user.is_authenticated:
            # Dashboard específico según el rol
            if user.rol == 'cliente':
                try:
                    from clientes.models import Pedido
                    context['mis_pedidos_recientes'] = Pedido.objects.filter(cliente=user).order_by('-fecha_pedido')[:5]
                except (ImportError, Exception):
                    context['mis_pedidos_recientes'] = []
            
            elif user.rol in ['vendedor', 'gerente', 'admin']:
                try:
                    from ventas.models import Venta
                    from clientes.models import Pedido
                    from inventario.models import Producto
                    
                    hoy = timezone.now().date()
                    hace_30_dias = hoy - timedelta(days=30)
                    
                    context.update({
                        'ventas_hoy': Venta.objects.filter(fecha_venta__date=hoy).count(),
                        'ventas_mes': Venta.objects.filter(fecha_venta__date__gte=hace_30_dias).count(),
                        'ingresos_mes': Venta.objects.filter(
                            fecha_venta__date__gte=hace_30_dias,
                            estado='completada'
                        ).aggregate(total=Sum('total'))['total'] or 0,
                        'productos_bajo_stock': Producto.objects.filter(
                            stock__lte=F('stock_minimo'), activo=True
                        ).count(),
                        'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
                    })
                except (ImportError, Exception):
                    context.update({
                        'ventas_hoy': 0, 'ventas_mes': 0, 'ingresos_mes': 0,
                        'productos_bajo_stock': 0, 'pedidos_pendientes': 0
                    })
        
        return context