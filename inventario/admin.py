from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, MovimientoInventario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'total_productos', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    
    def total_productos(self, obj):
        return obj.productos.count()
    total_productos.short_description = 'Total Productos'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre', 
        'categoria',
        'precio_formateado',
        'stock_badge',
        'activo',
        'fecha_creacion'
    )
    list_filter = (
        'categoria',
        'activo', 
        'fecha_creacion'
    )
    search_fields = ('codigo', 'nombre', 'descripcion')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria')
        }),
        ('Precio y Stock', {
            'fields': ('precio', 'stock', 'stock_minimo')
        }),
        ('Imagen y Estado', {
            'fields': ('imagen', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def precio_formateado(self, obj):
        return f"${obj.precio:,.0f}"
    precio_formateado.short_description = 'Precio'
    
    def stock_badge(self, obj):
        if obj.necesita_reabastecimiento:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔴 {} (Bajo stock)</span>',
                obj.stock
            )
        elif obj.stock == 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">❌ Sin stock</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ {}</span>',
                obj.stock
            )
    stock_badge.short_description = 'Stock'

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'producto', 
        'tipo_badge',
        'cantidad',
        'motivo',
        'usuario'
    )
    list_filter = ('tipo', 'fecha', 'producto__categoria')
    search_fields = ('producto__nombre', 'producto__codigo', 'motivo')
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)
    
    def tipo_badge(self, obj):
        colors = {
            'entrada': 'green',
            'salida': 'red',
            'ajuste': 'blue'
        }
        icons = {
            'entrada': '⬆️',
            'salida': '⬇️', 
            'ajuste': '🔄'
        }
        color = colors.get(obj.tipo, 'gray')
        icon = icons.get(obj.tipo, '❓')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'