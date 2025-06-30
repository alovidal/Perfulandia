from django import forms
from .models import Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ('cliente', 'descuento', 'metodo_pago', 'notas')
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }