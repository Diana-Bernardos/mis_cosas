from django.db import models
from django.conf import settings

# Create your models here.
class Tarea(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
