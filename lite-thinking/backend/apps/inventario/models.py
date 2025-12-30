"""
Modelos Django para la app Inventario
Mapea las entidades de dominio a la base de datos PostgreSQL
"""
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Inventario(models.Model):
    """
    Modelo Django que persiste la entidad de dominio Inventario
    Representa el stock de un producto en una ubicación
    """
    
    # Relación con Producto
    producto = models.OneToOneField(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='inventario',
        verbose_name="Producto",
        help_text="Producto del cual se lleva inventario"
    )
    
    cantidad_actual = models.IntegerField(
        default=0,
        verbose_name="Cantidad Actual",
        help_text="Cantidad física en inventario"
    )
    
    cantidad_reservada = models.IntegerField(
        default=0,
        verbose_name="Cantidad Reservada",
        help_text="Cantidad reservada para pedidos"
    )
    
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ubicación",
        help_text="Ubicación física en bodega (Ej: A-12-3)"
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
            models.CheckConstraint(
                check=models.Q(cantidad_reservada__gte=0),
                name='cantidad_reservada_no_negativa'
            ),
        ]
    
    def __str__(self):
        return f"Inventario: {self.producto.codigo} - Stock: {self.cantidad_actual}"
    
    def save(self, *args, **kwargs):
        """Override save para validar usando la entidad de dominio"""
        try:
            from dominio.entidades import Inventario as InventarioDominio
            
            entidad = InventarioDominio(
                producto_id=self.producto_id,
                cantidad_actual=self.cantidad_actual,
                cantidad_reservada=self.cantidad_reservada,
                ubicacion=self.ubicacion or ""
            )
            super().save(*args, **kwargs)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def to_domain(self):
        """Convierte el modelo Django a entidad de dominio"""
        from dominio.entidades import Inventario as InventarioDominio
        
        return InventarioDominio(
            id=self.id,
            producto_id=self.producto_id,
            cantidad_actual=self.cantidad_actual,
            cantidad_reservada=self.cantidad_reservada,
            ubicacion=self.ubicacion or "",
            fecha_creacion=self.created_at,
            fecha_actualizacion=self.updated_at
        )
    
    @property
    def cantidad_disponible(self):
        """Calcula cantidad disponible usando la entidad de dominio"""
        entidad = self.to_domain()
        return entidad.cantidad_disponible()
    
    @property
    def requiere_reabastecimiento(self):
        """Verifica si requiere reabastecimiento"""
        return self.cantidad_disponible <= self.producto.stock_minimo
    
    def registrar_entrada(self, cantidad, motivo="", usuario=None):
        """Registra una entrada de inventario"""
        movimiento = MovimientoInventario.objects.create(
            inventario=self,
            tipo='entrada',
            cantidad=cantidad,
            motivo=motivo,
            usuario=usuario
        )
        self.cantidad_actual += cantidad
        self.save()
        return movimiento
    
    def registrar_salida(self, cantidad, motivo="", usuario=None):
        """Registra una salida de inventario"""
        if self.cantidad_disponible < cantidad:
            raise ValidationError("Stock insuficiente")
        
        movimiento = MovimientoInventario.objects.create(
            inventario=self,
            tipo='salida',
            cantidad=cantidad,
            motivo=motivo,
            usuario=usuario
        )
        self.cantidad_actual -= cantidad
        self.save()
        return movimiento
    
    def ajustar_inventario(self, nueva_cantidad, motivo="", usuario=None):
        """Ajusta el inventario a una cantidad específica"""
        diferencia = nueva_cantidad - self.cantidad_actual
        
        MovimientoInventario.objects.create(
            inventario=self,
            tipo='ajuste',
            cantidad=abs(diferencia),
            motivo=motivo,
            usuario=usuario
        )
        self.cantidad_actual = nueva_cantidad
        self.save()
    
    def reservar(self, cantidad):
        """Reserva una cantidad de inventario"""
        if self.cantidad_disponible < cantidad:
            raise ValidationError("Stock disponible insuficiente para reservar")
        
        self.cantidad_reservada += cantidad
        self.save()
    
    def liberar_reserva(self, cantidad):
        """Libera una reserva de inventario"""
        if self.cantidad_reservada < cantidad:
            raise ValidationError("No hay suficiente cantidad reservada")
        
        self.cantidad_reservada -= cantidad
        self.save()


class MovimientoInventario(models.Model):
    """
    Modelo Django que persiste la entidad de dominio MovimientoInventario
    Registra todos los movimientos de inventario
    """
    
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
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
        verbose_name="Cantidad",
        help_text="Cantidad del movimiento"
    )
    
    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo",
        help_text="Razón del movimiento"
    )
    
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario",
        help_text="Usuario que realizó el movimiento"
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
    
    def save(self, *args, **kwargs):
        """Override save para validar usando la entidad de dominio"""
        try:
            from dominio.entidades import MovimientoInventario as MovimientoDominio, TipoMovimiento
            
            entidad = MovimientoDominio(
                inventario_id=self.inventario_id,
                tipo=TipoMovimiento(self.tipo),
                cantidad=self.cantidad,
                motivo=self.motivo or ""
            )
            super().save(*args, **kwargs)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def to_domain(self):
        """Convierte el modelo Django a entidad de dominio"""
        from dominio.entidades import MovimientoInventario as MovimientoDominio, TipoMovimiento
        
        return MovimientoDominio(
            id=self.id,
            inventario_id=self.inventario_id,
            tipo=TipoMovimiento(self.tipo),
            cantidad=self.cantidad,
            motivo=self.motivo or "",
            fecha=self.fecha
        )
