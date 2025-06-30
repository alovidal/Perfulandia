from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'clientes'

router = DefaultRouter()
router.register('pedidos', views.PedidoViewSet)

urlpatterns = [
    path('catalogo/', views.CatalogoProductosView.as_view(), name='catalogo'),
    path('producto/<uuid:pk>/', views.ProductoDetailView.as_view(), name='producto_detalle'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('agregar-carrito/<uuid:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('procesar-pedido/', views.procesar_pedido, name='procesar_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('api/', include(router.urls)),
]