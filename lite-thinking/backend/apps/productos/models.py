"""
Modelos Django para la app Productos
Incluye generación automática de códigos
"""
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


def generar_codigo_producto(nombre):
    """
    Genera código automático: 2 letras del nombre + número secuencial
    Ejemplo: "Laptop" -> "LA-001", "Mouse" -> "MO-002"
    """
    # Obtener las 2 primeras letras del nombre (en mayúsculas)
    prefijo = nombre[:2].upper() if len(nombre) >= 2 else nombre.upper()
    
    # Buscar el último código con ese prefijo
    from django.db.models import Max
    ultimo_codigo = Producto.objects.filter(
        codigo__startswith=f"{prefijo}-"
    ).aggregate(Max('codigo'))['codigo__max']
    
    if ultimo_codigo:
        # Extraer el número y sumar 1
        try:
            ultimo_numero = int(ultimo_codigo.split('-')[1])
            nuevo_numero = ultimo_numero + 1
        except (IndexError, ValueError):
            nuevo_numero = 1
    else:
        nuevo_numero = 1
    
    # Generar código con formato: XX-NNN
    return f"{prefijo}-{nuevo_numero:03d}"


class Producto(models.Model):
    """
    Modelo Django que persiste la entidad de dominio Producto
    """
    
    # Relación con Empresa
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Empresa",
        help_text="Empresa a la que pertenece el producto"
    )
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,  # ← Permitir vacío para generación automática
        verbose_name="Código",
        help_text="Código único del producto (se genera automáticamente si está vacío)"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre descriptivo del producto"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada del producto"
    )
    
    precio_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Precio USD",
        help_text="Precio del producto en dólares estadounidenses"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('fisico', 'Físico'),
            ('digital', 'Digital'),
            ('servicio', 'Servicio')
        ],
        default='fisico',
        verbose_name="Tipo de Producto"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el producto está activo para venta"
    )
    
    stock_minimo = models.IntegerField(
        default=0,
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima de stock antes de reabastecimiento"
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
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
        db_table = 'productos'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['empresa', 'activo']),
            models.Index(fields=['tipo']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(precio_usd__gt=0),
                name='precio_usd_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(stock_minimo__gte=0),
                name='stock_minimo_no_negativo'
            ),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Override save para:
        1. Generar código automáticamente si está vacío
        2. Validar usando la entidad de dominio
        """
        # 1. Generar código automático si está vacío
        if not self.codigo:
            self.codigo = generar_codigo_producto(self.nombre)
        
        # 2. Validar usando entidad de dominio
        try:
            from dominio.entidades import Producto as ProductoDominio
            
            entidad = ProductoDominio(
                codigo=self.codigo,
                nombre=self.nombre,
                descripcion=self.descripcion,
                precio_usd=Decimal(str(self.precio_usd)),
                empresa_id=self.empresa_id,
                tipo=self.tipo,
                activo=self.activo,
                stock_minimo=self.stock_minimo
            )
            # Si la validación pasa, guardar
            super().save(*args, **kwargs)
        except ValueError as e:
            # Convertir excepciones de dominio a excepciones de Django
            raise ValidationError(str(e))
    
    def to_domain(self):
        """Convierte el modelo Django a entidad de dominio"""
        from dominio.entidades import Producto as ProductoDominio, TipoProducto
        
        return ProductoDominio(
            id=self.id,
            codigo=self.codigo,
            nombre=self.nombre,
            descripcion=self.descripcion,
            precio_usd=self.precio_usd,
            empresa_id=self.empresa_id,
            tipo=TipoProducto(self.tipo),
            activo=self.activo,
            stock_minimo=self.stock_minimo,
            fecha_creacion=self.created_at,
            fecha_actualizacion=self.updated_at
        )
    
    @classmethod
    def from_domain(cls, entidad, empresa):
        """Crea un modelo Django desde una entidad de dominio"""
        return cls(
            id=entidad.id,
            empresa=empresa,
            codigo=entidad.codigo,
            nombre=entidad.nombre,
            descripcion=entidad.descripcion,
            precio_usd=entidad.precio_usd,
            tipo=entidad.tipo.value,
            activo=entidad.activo,
            stock_minimo=entidad.stock_minimo
        )
    
    def calcular_precio_cop(self, tasa_cambio: Decimal) -> Decimal:
        """Calcula el precio en pesos colombianos"""
        entidad = self.to_domain()
        return entidad.calcular_precio_cop(tasa_cambio)
    
    def calcular_precio_eur(self, tasa_cambio_usd_eur: Decimal) -> Decimal:
        """Calcula el precio en euros"""
        entidad = self.to_domain()
        return entidad.calcular_precio_eur(tasa_cambio_usd_eur)
    
    def requiere_reabastecimiento(self, stock_actual: int) -> bool:
        """Verifica si requiere reabastecimiento"""
        entidad = self.to_domain()
        return entidad.requiere_reabastecimiento(stock_actual)