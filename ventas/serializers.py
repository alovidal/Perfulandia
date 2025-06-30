from rest_framework import serializers
from .models import Venta, DetalleVenta, Factura

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.get_full_name', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.get_full_name', read_only=True)
    
    class Meta:
        model = Venta
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    venta_numero = serializers.CharField(source='venta.numero_venta', read_only=True)
    
    class Meta:
        model = Factura
        fields = '__all__'