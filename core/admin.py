from django.contrib import admin
from django.utils.html import format_html
from .models import Auditoria

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'usuario',
        'accion_badge',
        'tabla', 
        'registro_id',
        'ip_address'
    )
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = (
        'usuario__username',
        'accion',
        'tabla',
        'registro_id'
    )
    ordering = ('-fecha',)
    readonly_fields = (
        'usuario',
        'accion', 
        'tabla',
        'registro_id',
        'detalles',
        'fecha',
        'ip_address'
    )
    
    def has_add_permission(self, request):
        return False  # No permitir agregar auditorías manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar auditorías
    
    def accion_badge(self, obj):
        colors = {
            'CREATE': 'green',
            'UPDATE': 'blue', 
            'DELETE': 'red',
            'LOGIN': 'purple'
        }
        color = colors.get(obj.accion, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.accion
        )
    accion_badge.short_description = 'Acción'
