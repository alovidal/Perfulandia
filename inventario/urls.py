from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventario'

router = DefaultRouter()
router.register('productos', views.ProductoViewSet)

urlpatterns = [
    path('productos/', views.ProductosListView.as_view(), name='productos'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/editar/<uuid:pk>/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('movimientos/', views.MovimientosInventarioView.as_view(), name='movimientos'),
    path('api/', include(router.urls)),
]
