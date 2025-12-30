"""
Modelos Django para la app Empresas
Mapea las entidades de dominio a la base de datos PostgreSQL
"""
from django.db import models
from dominio.entidades import Empresa as EmpresaDominio


class Empresa(models.Model):
    """
    Modelo Django que persiste la entidad de dominio Empresa
    Mantiene la lógica de negocio en el dominio
    """
    nit = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="NIT",
        help_text="Número de Identificación Tributaria"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Razón social de la empresa"
    )
    direccion = models.TextField(
        verbose_name="Dirección",
        help_text="Dirección física de la empresa"
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Número de contacto principal"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Correo electrónico de contacto"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la empresa está activa en el sistema"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['-created_at']
        db_table = 'empresas'
        indexes = [
            models.Index(fields=['nit']),
            models.Index(fields=['nombre']),
            models.Index(fields=['activa']),
        ]
    
    def __str__(self):
        return f"{self.nit} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Override save para validar usando la entidad de dominio
        """
        # Crear entidad de dominio para validación
        try:
            entidad = EmpresaDominio(
                nit=self.nit,
                nombre=self.nombre,
                direccion=self.direccion,
                telefono=self.telefono,
                email=self.email,
                activa=self.activa
            )
            # Si la validación pasa, guardar
            super().save(*args, **kwargs)
        except ValueError as e:
            # Convertir excepciones de dominio a excepciones de Django
            from django.core.exceptions import ValidationError
            raise ValidationError(str(e))
    
    def to_domain(self) -> EmpresaDominio:
        """
        Convierte el modelo Django a entidad de dominio
        Returns:
            EmpresaDominio: Entidad de dominio con las reglas de negocio
        """
        return EmpresaDominio(
            id=self.id,
            nit=self.nit,
            nombre=self.nombre,
            direccion=self.direccion,
            telefono=self.telefono,
            email=self.email,
            activa=self.activa,
            fecha_creacion=self.created_at,
            fecha_actualizacion=self.updated_at
        )
    
    @classmethod
    def from_domain(cls, entidad: EmpresaDominio):
        """
        Crea un modelo Django desde una entidad de dominio
        Args:
            entidad: Entidad de dominio Empresa
        Returns:
            Empresa: Instancia del modelo Django
        """
        return cls(
            id=entidad.id,
            nit=entidad.nit,
            nombre=entidad.nombre,
            direccion=entidad.direccion,
            telefono=entidad.telefono,
            email=entidad.email,
            activa=entidad.activa
        )
