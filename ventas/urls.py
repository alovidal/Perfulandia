from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentasListView.as_view(), name='lista'),
    path('registrar/', views.RegistrarVentaView.as_view(), name='registrar'),
    path('detalle/<int:pk>/', views.VentaDetalleView.as_view(), name='detalle'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('facturas/', views.FacturasListView.as_view(), name='facturas'),
]