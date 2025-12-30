"""
Entidad Producto - Dominio Puro
Sin dependencias de Django o frameworks externos
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum


class TipoProducto(Enum):
    """Tipos de producto soportados"""
    FISICO = "fisico"
    DIGITAL = "digital"
    SERVICIO = "servicio"


@dataclass
class Producto:
    """
    Entidad de dominio que representa un Producto
    Reglas de negocio puras sin lógica de persistencia
    """
    codigo: str
    nombre: str
    descripcion: str
    precio_usd: Decimal
    empresa_id: int
    tipo: TipoProducto = TipoProducto.FISICO
    activo: bool = True
    stock_minimo: int = 0
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones de dominio al crear la entidad"""
        # Convertir string a enum si es necesario
        if isinstance(self.tipo, str):
            self.tipo = TipoProducto(self.tipo)
        
        # Asegurar que precio_usd sea Decimal
        if not isinstance(self.precio_usd, Decimal):
            self.precio_usd = Decimal(str(self.precio_usd))
        
        self.validar()

    def validar(self) -> None:
        """
        Validaciones de reglas de negocio
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.codigo or len(self.codigo.strip()) == 0:
            raise ValueError("El código es obligatorio")
        
        if len(self.codigo) > 50:
            raise ValueError("El código no puede exceder 50 caracteres")
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        
        if len(self.nombre) > 200:
            raise ValueError("El nombre no puede exceder 200 caracteres")
        
        if self.precio_usd <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        
        if self.precio_usd > Decimal('999999999.99'):
            raise ValueError("El precio excede el límite permitido")
        
        if self.stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo")
        
        if not self.empresa_id or self.empresa_id <= 0:
            raise ValueError("Debe especificar una empresa válida")

    def calcular_precio_cop(self, tasa_cambio: Decimal) -> Decimal:
        """
        Calcula el precio en pesos colombianos
        Args:
            tasa_cambio: Tasa de cambio USD a COP
        Returns:
            Precio en COP
        """
        if tasa_cambio <= 0:
            raise ValueError("La tasa de cambio debe ser mayor a 0")
        return self.precio_usd * tasa_cambio

    def calcular_precio_eur(self, tasa_cambio_usd_eur: Decimal) -> Decimal:
        """
        Calcula el precio en euros
        Args:
            tasa_cambio_usd_eur: Tasa de cambio USD a EUR
        Returns:
            Precio en EUR
        """
        if tasa_cambio_usd_eur <= 0:
            raise ValueError("La tasa de cambio debe ser mayor a 0")
        return self.precio_usd * tasa_cambio_usd_eur

    def actualizar_precio(self, nuevo_precio_usd: Decimal) -> None:
        """
        Actualiza el precio del producto
        Args:
            nuevo_precio_usd: Nuevo precio en USD
        """
        if nuevo_precio_usd <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        
        self.precio_usd = nuevo_precio_usd
        self.fecha_actualizacion = datetime.now()

    def activar(self) -> None:
        """Activa el producto"""
        self.activo = True
        self.fecha_actualizacion = datetime.now()

    def desactivar(self) -> None:
        """Desactiva el producto"""
        self.activo = False
        self.fecha_actualizacion = datetime.now()

    def requiere_reabastecimiento(self, stock_actual: int) -> bool:
        """
        Verifica si el producto requiere reabastecimiento
        Args:
            stock_actual: Cantidad actual en inventario
        Returns:
            True si requiere reabastecimiento
        """
        return stock_actual <= self.stock_minimo

    def __str__(self) -> str:
        return f"Producto({self.codigo} - {self.nombre})"

    def __repr__(self) -> str:
        return (
            f"Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}', "
            f"precio_usd={self.precio_usd}, activo={self.activo})"
        )
