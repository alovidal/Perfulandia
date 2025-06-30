from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Producto, Categoria, MovimientoInventario
from .forms import ProductoForm, CategoriaForm, MovimientoInventarioForm
from .serializers import ProductoSerializer, CategoriaSerializer
from core.permissions import RolRequeridoMixin

class ProductosListView(RolRequeridoMixin, ListView):
    model = Producto
    template_name = 'inventario/productos_list.html'
    context_object_name = 'productos'
    roles_permitidos = ['gerente', 'admin', 'vendedor']
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Producto.objects.all().order_by('nombre')
        
        # Filtros
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(codigo__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )
        
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        if self.request.GET.get('bajo_stock'):
            queryset = queryset.filter(stock__lte=F('stock_minimo'))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(activa=True)
        context['productos_bajo_stock'] = Producto.objects.filter(
            stock__lte=F('stock_minimo')
        ).count()
        return context

class ProductoCreateView(RolRequeridoMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario:productos')
    roles_permitidos = ['gerente', 'admin']
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar movimiento de inventario inicial
        if self.object.stock > 0:
            MovimientoInventario.objects.create(
                producto=self.object,
                tipo='entrada',
                cantidad=self.object.stock,
                motivo='Stock inicial',
                usuario=self.request.user
            )
        
        messages.success(self.request, 'Producto creado exitosamente.')
        return response

class ProductoUpdateView(RolRequeridoMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario:productos')
    roles_permitidos = ['gerente', 'admin']
    
    def form_valid(self, form):
        stock_anterior = Producto.objects.get(id=self.object.id).stock
        response = super().form_valid(form)
        
        # Registrar movimiento si cambió el stock
        diferencia = self.object.stock - stock_anterior
        if diferencia != 0:
            MovimientoInventario.objects.create(
                producto=self.object,
                tipo='entrada' if diferencia > 0 else 'salida',
                cantidad=abs(diferencia),
                motivo='Ajuste manual',
                usuario=self.request.user
            )
        
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return response

class MovimientosInventarioView(RolRequeridoMixin, ListView):
    model = MovimientoInventario
    template_name = 'inventario/movimientos.html'
    context_object_name = 'movimientos'
    roles_permitidos = ['gerente', 'admin']
    paginate_by = 50
    
    def get_queryset(self):
        return MovimientoInventario.objects.select_related(
            'producto', 'usuario'
        ).order_by('-fecha')

# API ViewSets
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        productos = self.queryset.filter(stock__lte=F('stock_minimo'))
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ajustar_stock(self, request, pk=None):
        producto = self.get_object()
        cantidad = request.data.get('cantidad')
        motivo = request.data.get('motivo', 'Ajuste vía API')
        
        if cantidad is None:
            return Response({'error': 'Cantidad requerida'}, status=400)
        
        cantidad = int(cantidad)
        stock_anterior = producto.stock
        producto.stock = max(0, producto.stock + cantidad)
        producto.save()
        
        # Registrar movimiento
        MovimientoInventario.objects.create(
            producto=producto,
            tipo='entrada' if cantidad > 0 else 'salida',
            cantidad=abs(cantidad),
            motivo=motivo,
            usuario=request.user
        )
        
        return Response({
            'stock_anterior': stock_anterior,
            'stock_actual': producto.stock,
            'cantidad_ajustada': cantidad
        })
