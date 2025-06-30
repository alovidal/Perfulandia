from django.db import models
from usuarios.models import Usuario
from inventario.models import Producto
from clientes.models import Pedido
import uuid

class Venta(models.Model):
    TIPOS = [
        ('presencial', 'Venta Presencial'),
        ('online', 'Venta Online'),
    ]
    
    ESTADOS = [
        ('completada', 'Completada'),
        ('pendiente', 'Pendiente'),
        ('cancelada', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_venta = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='completada')
    vendedor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='ventas_realizadas')
    cliente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas_cliente')
    pedido = models.OneToOneField(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, default='efectivo')
    notas = models.TextField(blank=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta {self.numero_venta} - {self.fecha_venta.strftime('%d/%m/%Y')}"

class DetalleVenta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

class Factura(models.Model):
    TIPOS = [
        ('boleta', 'Boleta'),
        ('factura', 'Factura'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_factura = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='factura')
    cliente_nombre = models.CharField(max_length=200)
    cliente_rut = models.CharField(max_length=12, blank=True)
    cliente_direccion = models.TextField(blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='facturas/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"Factura {self.numero_factura}"
