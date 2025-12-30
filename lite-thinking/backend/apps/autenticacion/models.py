"""
Modelos Django para Autenticación - SIN RELACIÓN CON EMPRESAS
Solo tipos: Administrador y Externo
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo Django que extiende AbstractUser
    - Administrador: Acceso completo (CRUD)
    - Externo: Solo lectura
    - NO hay relación con empresas
    """
    
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('externo', 'Externo'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='administrador',
        verbose_name="Tipo de Usuario",
        help_text="Administrador: acceso completo | Externo: solo visualización"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Usuario Activo"
    )
    
    fecha_ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Acceso"
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = 'usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['tipo']),
        ]
    
    @property
    def nombre_completo(self):
        """Retorna nombre completo"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def es_administrador(self):
        """Verifica si es administrador"""
        return self.tipo == 'administrador'
    
    @property
    def es_externo(self):
        """Verifica si es externo"""
        return self.tipo == 'externo'
    
    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"