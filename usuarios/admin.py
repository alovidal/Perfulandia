from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'rut')
    ordering = ('-fecha_creacion',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'direccion')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': (
                'email',
                'first_name', 
                'last_name',
                'rol',
                'telefono'
            )
        }),
    )
    
    def rol_badge(self, obj):
        colors = {
            'admin': 'red',
            'gerente': 'blue', 
            'vendedor': 'green',
            'cliente': 'gray'
        }
        color = colors.get(obj.rol, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_rol_display()
        )
    rol_badge.short_description = 'Rol'

admin.site.register(Usuario, CustomUserAdmin)
