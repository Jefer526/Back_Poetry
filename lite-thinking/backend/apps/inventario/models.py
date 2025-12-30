"""
Modelos Django para Inventario - VERSIÓN FINAL SIMPLE
Sin cantidad_reservada, solo entrada y salida
"""
from django.db import models
from django.core.exceptions import ValidationError


class Inventario(models.Model):
    """Modelo Django para Inventario"""
    
    producto = models.OneToOneField(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='inventario',
        verbose_name="Producto"
    )
    
    cantidad_actual = models.IntegerField(
        default=0,
        verbose_name="Cantidad en Stock"
    )
    
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ubicación",
        help_text="Ubicación física en bodega (Ej: A-12-3)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        ordering = ['-created_at']
        db_table = 'inventarios'
        indexes = [
            models.Index(fields=['producto']),
            models.Index(fields=['cantidad_actual']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad_actual__gte=0),
                name='cantidad_actual_no_negativa'
            ),
        ]
    
    def __str__(self):
        return f"Inventario: {self.producto.codigo} - Stock: {self.cantidad_actual}"
    
    @property
    def requiere_reabastecimiento(self):
        """Verifica si requiere reabastecimiento"""
        return self.cantidad_actual <= self.producto.stock_minimo


class MovimientoInventario(models.Model):
    """
    Modelo Django para MovimientoInventario
    SOLO ENTRADA Y SALIDA
    """
    
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name="Inventario"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    
    cantidad = models.IntegerField(
        verbose_name="Cantidad"
    )
    
    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo"
    )
    
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Movimiento"
    )
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
        db_table = 'movimientos_inventario'
        indexes = [
            models.Index(fields=['inventario', '-fecha']),
            models.Index(fields=['tipo']),
            models.Index(fields=['fecha']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad__gt=0),
                name='cantidad_movimiento_positiva'
            ),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cantidad} - {self.inventario.producto.codigo}"