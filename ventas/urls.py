from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ventas'

router = DefaultRouter()
router.register('ventas', views.VentaViewSet)

urlpatterns = [
    path('lista/', views.VentasListView.as_view(), name='lista'),
    path('registrar/', views.RegistrarVentaView.as_view(), name='registrar'),
    path('detalle/<uuid:pk>/', views.VentaDetailView.as_view(), name='detalle'),
    path('factura/<uuid:venta_id>/pdf/', views.generar_factura_pdf, name='factura_pdf'),
    path('api/', include(router.urls)),
]