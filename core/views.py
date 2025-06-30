from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count, Sum, Q, F  # ← Agregar import F
from django.utils import timezone
from datetime import timedelta

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Dashboard según rol del usuario
        if user.rol == 'cliente':
            try:
                from inventario.models import Producto
                from clientes.models import Pedido
                context.update({
                    'productos_destacados': Producto.objects.filter(activo=True)[:8],
                    'mis_pedidos_recientes': Pedido.objects.filter(cliente=user)[:5],
                })
            except ImportError:
                context.update({
                    'productos_destacados': [],
                    'mis_pedidos_recientes': [],
                })
        
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
                        stock__lte=F('stock_minimo')
                    ).count(),
                    'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
                })
            except ImportError:
                context.update({
                    'ventas_hoy': 0,
                    'ventas_mes': 0,
                    'ingresos_mes': 0,
                    'productos_bajo_stock': 0,
                    'pedidos_pendientes': 0,
                })
        
        return context