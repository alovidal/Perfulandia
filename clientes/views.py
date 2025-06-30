from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from inventario.models import Producto, Categoria
from .models import CarritoCompra, ItemCarrito, Pedido, DetallePedido
from .forms import PedidoForm
from .serializers import PedidoSerializer, CarritoCompraSerializer
from core.permissions import RolRequeridoMixin

class CatalogoProductosView(ListView):
    model = Producto
    template_name = 'clientes/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True, stock__gt=0)
        
        # Filtros
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(descripcion__icontains=busqueda) |
                Q(codigo__icontains=busqueda)
            )
        
        orden = self.request.GET.get('orden', 'nombre')
        if orden == 'precio_asc':
            queryset = queryset.order_by('precio')
        elif orden == 'precio_desc':
            queryset = queryset.order_by('-precio')
        else:
            queryset = queryset.order_by('nombre')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(activa=True)
        return context

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'clientes/producto_detalle.html'
    context_object_name = 'producto'

@login_required
def agregar_al_carrito(request, producto_id):
    if request.user.rol != 'cliente':
        return JsonResponse({'error': 'Solo los clientes pueden agregar productos al carrito'}, status=403)
    
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad > producto.stock:
        return JsonResponse({'error': 'Stock insuficiente'}, status=400)
    
    carrito, created = CarritoCompra.objects.get_or_create(cliente=request.user)
    
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad, 'precio_unitario': producto.precio}
    )
    
    if not created:
        nueva_cantidad = item.cantidad + cantidad
        if nueva_cantidad > producto.stock:
            return JsonResponse({'error': 'Stock insuficiente'}, status=400)
        item.cantidad = nueva_cantidad
        item.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Producto agregado al carrito',
        'total_items': carrito.total_items
    })

@login_required
def ver_carrito(request):
    if request.user.rol != 'cliente':
        messages.error(request, 'Solo los clientes pueden ver el carrito.')
        return redirect('home')
    
    carrito, created = CarritoCompra.objects.get_or_create(cliente=request.user)
    return render(request, 'clientes/carrito.html', {'carrito': carrito})

@login_required
def procesar_pedido(request):
    if request.user.rol != 'cliente':
        return redirect('home')
    
    carrito = get_object_or_404(CarritoCompra, cliente=request.user)
    
    if not carrito.items.exists():
        messages.error(request, 'El carrito está vacío.')
        return redirect('clientes:carrito')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # Crear pedido
            pedido = Pedido.objects.create(
                numero_pedido=f"PED-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                cliente=request.user,
                total=carrito.total,
                direccion_entrega=form.cleaned_data['direccion_entrega'],
                telefono_contacto=form.cleaned_data['telefono_contacto'],
                notas=form.cleaned_data.get('notas', '')
            )
            
            # Crear detalles del pedido
            for item in carrito.items.all():
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.subtotal
                )
                
                # Actualizar stock
                item.producto.stock -= item.cantidad
                item.producto.save()
            
            # Limpiar carrito
            carrito.items.all().delete()
            
            messages.success(request, f'Pedido {pedido.numero_pedido} realizado exitosamente.')
            return redirect('clientes:mis_pedidos')
    else:
        form = PedidoForm()
    
    return render(request, 'clientes/procesar_pedido.html', {
        'form': form,
        'carrito': carrito
    })

@login_required
def mis_pedidos(request):
    if request.user.rol != 'cliente':
        return redirect('home')
    
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    return render(request, 'clientes/mis_pedidos.html', {'pedidos': pedidos})

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
