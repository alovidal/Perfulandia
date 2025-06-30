from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.ventas_list_view, name='lista'),
    path('detalle/<uuid:pk>/', views.VentaDetailView.as_view(), name='detalle'),
    path('factura/<uuid:venta_id>/pdf/', views.generar_factura_pdf, name='factura_pdf'),
    
    # La ruta a 'registrar' se ha comentado porque la vista 'RegistrarVentaView' fue eliminada.
    # Para que el botón "Registrar Venta" funcione, se necesita crear una nueva vista.
    # path('registrar/', views.tu_nueva_vista_registrar, name='registrar'),
]