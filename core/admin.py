from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models import Usuario  # ← Corregir importación
from .models import Auditoria

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'fecha_creacion')
    list_filter = ('rol', 'is_active', 'fecha_creacion')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol',)
        }),
    )

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'tabla', 'fecha')
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = ('usuario__username', 'accion', 'tabla')
    readonly_fields = ('usuario', 'accion', 'tabla', 'registro_id', 'detalles', 'fecha', 'ip_address')
