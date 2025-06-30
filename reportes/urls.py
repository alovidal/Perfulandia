from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('ventas/', views.reporte_ventas, name='ventas'),
    path('inventario/', views.reporte_inventario, name='inventario'),
    # Apuntando temporalmente a dashboard para evitar errores
    path('clientes/', views.dashboard_view, name='clientes'),
    path('financiero/', views.dashboard_view, name='financiero'),
]
