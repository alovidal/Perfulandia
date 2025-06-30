from django.contrib import admin
from django.utils.html import format_html
from .models import CarritoCompra, ItemCarrito, Pedido, DetallePedido

@admin.register(CarritoCompra)
class CarritoCompraAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'total_items_display',
        'total_formateado', 
        'fecha_actualizacion'
    )
    list_filter = ('fecha_creacion', 'fecha_actualizacion')
    search_fields = ('cliente__username', 'cliente__email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def total_items_display(self, obj):
        return f"{obj.total_items} items"
    total_items_display.short_description = 'Items'
    
    def total_formateado(self, obj):
        return f"${obj.total:,.0f}"
    total_formateado.short_description = 'Total'

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = (
        'carrito_cliente',
        'producto', 
        'cantidad',
        'precio_unitario',
        'subtotal_formateado'
    )
    list_filter = ('fecha_agregado',)
    search_fields = (
        'carrito__cliente__username',
        'producto__nombre',
        'producto__codigo'
    )
    
    def carrito_cliente(self, obj):
        return obj.carrito.cliente.username
    carrito_cliente.short_description = 'Cliente'
    
    def subtotal_formateado(self, obj):
        return f"${obj.subtotal:,.0f}"
    subtotal_formateado.short_description = 'Subtotal'

# PRIMERO definir el Inline, DESPUÉS usarlo
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

# AHORA sí definir PedidoAdmin con el inline
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_pedido',
        'cliente',
        'estado_badge',
        'total_formateado',
        'fecha_pedido'
    )
    list_filter = ('estado', 'fecha_pedido')
    search_fields = (
        'numero_pedido',
        'cliente__username',
        'cliente__email'
    )
    ordering = ('-fecha_pedido',)
    readonly_fields = ('numero_pedido', 'fecha_pedido')
    
    # CORRECCIÓN: Sin comillas, es una referencia a la clase
    inlines = [DetallePedidoInline]
    
    def estado_badge(self, obj):
        colors = {
            'pendiente': 'orange',
            'procesando': 'blue',
            'enviado': 'purple',
            'entregado': 'green',
            'cancelado': 'red'
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

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = (
        'pedido_numero',
        'producto',
        'cantidad', 
        'precio_unitario',
        'subtotal_formateado'
    )
    list_filter = ('pedido__fecha_pedido',)
    search_fields = (
        'pedido__numero_pedido',
        'producto__nombre',
        'producto__codigo'
    )
    
    def pedido_numero(self, obj):
        return obj.pedido.numero_pedido
    pedido_numero.short_description = 'Pedido'
    
    def subtotal_formateado(self, obj):
        return f"${obj.subtotal:,.0f}"
    subtotal_formateado.short_description = 'Subtotal'
