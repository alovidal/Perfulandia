from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"
