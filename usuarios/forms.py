from django import forms
from django.contrib.auth.forms import UserCreationForm
from usuarios.models import Usuario

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'direccion')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
