from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario
from .forms import RegistroForm, PerfilForm, UsuarioForm
from .serializers import UsuarioSerializer
from core.permissions import RolRequeridoMixin, rol_requerido

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'cliente'  # Por defecto los registros son clientes
            user.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Perfulandia SPA.')
            return redirect('home')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'usuarios/perfil.html', {'form': form})

class GestionUsuariosListView(RolRequeridoMixin, ListView):
    model = Usuario
    template_name = 'usuarios/gestion_usuarios.html'
    context_object_name = 'usuarios'
    roles_permitidos = ['admin', 'gerente']
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Usuario.objects.all().order_by('-fecha_creacion')
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(username__icontains=busqueda) |
                Q(email__icontains=busqueda) |
                Q(first_name__icontains=busqueda) |
                Q(last_name__icontains=busqueda)
            )
        return queryset

class UsuarioCreateView(RolRequeridoMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:gestion')
    roles_permitidos = ['admin']

class UsuarioUpdateView(RolRequeridoMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuarios:gestion')
    roles_permitidos = ['admin']

# API ViewSet
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        rol = request.query_params.get('rol')
        if rol:
            usuarios = self.queryset.filter(rol=rol)
            serializer = self.get_serializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({'error': 'Rol requerido'}, status=status.HTTP_400_BAD_REQUEST)
