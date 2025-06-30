from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'usuarios'

router = DefaultRouter()
router.register('usuarios', views.UsuarioViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('gestion/', views.GestionUsuariosListView.as_view(), name='gestion'),
    path('crear/', views.UsuarioCreateView.as_view(), name='crear'),
    path('editar/<uuid:pk>/', views.UsuarioUpdateView.as_view(), name='editar'),
    path('api/', include(router.urls)),
]