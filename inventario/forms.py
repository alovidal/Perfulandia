from django import forms
from .models import Producto, Categoria, MovimientoInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('codigo', 'nombre', 'descripcion', 'categoria', 'precio', 'stock', 'stock_minimo', 'imagen', 'activo')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ('nombre', 'descripcion', 'activa')

class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ('producto', 'tipo', 'cantidad', 'motivo')