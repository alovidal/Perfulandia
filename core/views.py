from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from inventario.models import Producto
from ventas.models import Venta
from clientes.models import Pedido

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Dashboard según rol del usuario
        if user.rol == 'cliente':
            context.update({
                'productos_destacados': Producto.objects.filter(activo=True)[:8],
                'mis_pedidos_recientes': Pedido.objects.filter(cliente=user)[:5],
            })
        
        elif user.rol in ['vendedor', 'gerente', 'admin']:
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
                    stock__lte=models.F('stock_minimo')
                ).count(),
                'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
            })
        
        return context
