from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )
    
    # Cambiar a UUID como clave primaria si quieres consistencia
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    sucursal = models.CharField(max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.rol})"
