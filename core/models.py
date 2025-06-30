from django.db import models
from usuarios.models import Usuario  # ← Importar desde usuarios
import uuid

class Auditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    tabla = models.CharField(max_length=50)
    registro_id = models.CharField(max_length=100)
    detalles = models.JSONField(default=dict)
    fecha = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha']