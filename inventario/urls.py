from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('productos/', views.ProductosListView.as_view(), name='productos'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/editar/<uuid:pk>/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    
    path('categorias/', views.CategoriasListView.as_view(), name='categorias'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/editar/<int:pk>/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    
    path('movimientos/', views.MovimientosInventarioView.as_view(), name='movimientos'),
    path('stock-bajo/', views.StockBajoView.as_view(), name='stock_bajo'),
]
