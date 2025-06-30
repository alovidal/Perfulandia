from django.contrib import admin
from django.utils.html import format_html
from .models import Venta, DetalleVenta, Factura

# PRIMERO definir el Inline, DESPUÉS usarlo
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

# AHORA sí definir VentaAdmin con el inline
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_venta',
        'tipo_badge',
        'vendedor',
        'cliente',
        'estado_badge',
        'total_formateado',
        'fecha_venta'
    )
    list_filter = ('tipo', 'estado', 'fecha_venta', 'vendedor')
    search_fields = (
        'numero_venta',
        'vendedor__username',
        'cliente__username'
    )
    ordering = ('-fecha_venta',)
    readonly_fields = ('numero_venta', 'fecha_venta')
    
    # CORRECCIÓN: Sin comillas, es una referencia a la clase
    inlines = [DetalleVentaInline]
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': (
                'numero_venta',
                'tipo',
                'estado',
                'vendedor',
                'cliente',
                'pedido'
            )
        }),
        ('Montos', {
            'fields': (
                'subtotal',
                'impuesto', 
                'descuento',
                'total'
            )
        }),
        ('Detalles Adicionales', {
            'fields': (
                'metodo_pago',
                'notas',
                'fecha_venta'
            )
        })
    )
    
    def tipo_badge(self, obj):
        colors = {'presencial': 'blue', 'online': 'green'}
        color = colors.get(obj.tipo, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def estado_badge(self, obj):
        colors = {
            'completada': 'green',
            'pendiente': 'orange',
            'cancelada': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def total_formateado(self, obj):
        return f"${obj.total:,.0f}"
    total_formateado.short_description = 'Total'

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = (
        'venta_numero',
        'producto',
        'cantidad',
        'precio_unitario', 
        'subtotal_formateado'
    )
    list_filter = ('venta__fecha_venta',)
    search_fields = (
        'venta__numero_venta',
        'producto__nombre',
        'producto__codigo'
    )
    
    def venta_numero(self, obj):
        return obj.venta.numero_venta
    venta_numero.short_description = 'Venta'
    
    def subtotal_formateado(self, obj):
        return f"${obj.subtotal:,.0f}"
    subtotal_formateado.short_description = 'Subtotal'

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura',
        'tipo_badge',
        'venta_numero',
        'cliente_nombre',
        'fecha_emision',
        'tiene_pdf'
    )
    list_filter = ('tipo', 'fecha_emision')
    search_fields = (
        'numero_factura',
        'cliente_nombre',
        'cliente_rut',
        'venta__numero_venta'
    )
    ordering = ('-fecha_emision',)
    readonly_fields = ('fecha_emision',)
    
    def tipo_badge(self, obj):
        colors = {'boleta': 'blue', 'factura': 'green'}
        color = colors.get(obj.tipo, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def venta_numero(self, obj):
        return obj.venta.numero_venta
    venta_numero.short_description = 'Venta'
    
    def tiene_pdf(self, obj):
        if obj.archivo_pdf:
            return format_html(
                '<span style="color: green;">✅ Sí</span>'
            )
        return format_html(
            '<span style="color: red;">❌ No</span>'
        )
    tiene_pdf.short_description = 'PDF'
