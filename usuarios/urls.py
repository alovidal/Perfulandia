from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'usuarios'

router = DefaultRouter()
router.register('usuarios', views.UsuarioViewSet)

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/cambiar_password.html',
        success_url = reverse_lazy('usuarios:password_change_done')
    ), name='cambiar_password'),
    
    path('cambiar-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='usuarios/password_change_done.html'
    ), name='password_change_done'),

    path('gestion/', views.GestionUsuariosListView.as_view(), name='gestion'),
    path('crear/', views.UsuarioCreateView.as_view(), name='crear'),
    path('editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar'),
    
    path('api/', include(router.urls)),
]