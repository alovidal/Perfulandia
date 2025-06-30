from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('usuarios/', include('usuarios.urls')),
    path('clientes/', include('clientes.urls')),
    path('inventario/', include('inventario.urls')),
    path('ventas/', include('ventas.urls')),
    path('reportes/', include('reportes.urls')),
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Perfulandia SPA - Administración"
admin.site.site_title = "Perfulandia SPA"
admin.site.index_title = "Panel de Administración"