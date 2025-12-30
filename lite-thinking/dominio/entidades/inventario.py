"""
Entidades Inventario - Dominio Puro
Sin dependencias de Django o frameworks externos
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class TipoMovimiento(Enum):
    """Tipos de movimiento de inventario"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    DEVOLUCION = "devolucion"


@dataclass
class MovimientoInventario:
    """
    Representa un movimiento individual de inventario
    """
    tipo: TipoMovimiento
    cantidad: int
    motivo: str
    usuario_id: int
    fecha: datetime = field(default_factory=datetime.now)
    precio_unitario: Optional[Decimal] = None
    id: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.tipo, str):
            self.tipo = TipoMovimiento(self.tipo)
        self.validar()

    def validar(self) -> None:
        """Validaciones de reglas de negocio"""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if not self.motivo or len(self.motivo.strip()) == 0:
            raise ValueError("El motivo es obligatorio")
        
        if self.precio_unitario is not None and self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo")

    def calcular_valor_total(self) -> Decimal:
        """Calcula el valor total del movimiento"""
        if self.precio_unitario is None:
            return Decimal('0')
        return self.precio_unitario * Decimal(str(self.cantidad))


@dataclass
class Inventario:
    """
    Entidad de dominio que representa el Inventario de un producto
    Reglas de negocio puras sin lógica de persistencia
    """
    producto_id: int
    cantidad_actual: int
    cantidad_reservada: int = 0
    ubicacion: str = "ALMACEN-PRINCIPAL"
    lote: Optional[str] = None
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    
    # Historial de movimientos (no se persiste directamente)
    _movimientos: List[MovimientoInventario] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Validaciones de dominio al crear la entidad"""
        self.validar()

    def validar(self) -> None:
        """
        Validaciones de reglas de negocio
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.producto_id or self.producto_id <= 0:
            raise ValueError("Debe especificar un producto válido")
        
        if self.cantidad_actual < 0:
            raise ValueError("La cantidad actual no puede ser negativa")
        
        if self.cantidad_reservada < 0:
            raise ValueError("La cantidad reservada no puede ser negativa")
        
        if self.cantidad_reservada > self.cantidad_actual:
            raise ValueError("La cantidad reservada no puede ser mayor a la cantidad actual")

    def cantidad_disponible(self) -> int:
        """
        Calcula la cantidad disponible (no reservada)
        Returns:
            Cantidad disponible para venta
        """
        return self.cantidad_actual - self.cantidad_reservada

    def registrar_entrada(
        self,
        cantidad: int,
        motivo: str,
        usuario_id: int,
        precio_unitario: Optional[Decimal] = None
    ) -> MovimientoInventario:
        """
        Registra una entrada de inventario
        Args:
            cantidad: Cantidad a ingresar
            motivo: Motivo del ingreso
            usuario_id: ID del usuario que registra
            precio_unitario: Precio unitario opcional
        Returns:
            MovimientoInventario creado
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        movimiento = MovimientoInventario(
            tipo=TipoMovimiento.ENTRADA,
            cantidad=cantidad,
            motivo=motivo,
            usuario_id=usuario_id,
            precio_unitario=precio_unitario
        )
        
        self.cantidad_actual += cantidad
        self.fecha_actualizacion = datetime.now()
        self._movimientos.append(movimiento)
        
        return movimiento

    def registrar_salida(
        self,
        cantidad: int,
        motivo: str,
        usuario_id: int,
        verificar_disponibilidad: bool = True
    ) -> MovimientoInventario:
        """
        Registra una salida de inventario
        Args:
            cantidad: Cantidad a retirar
            motivo: Motivo de la salida
            usuario_id: ID del usuario que registra
            verificar_disponibilidad: Si debe verificar disponibilidad
        Returns:
            MovimientoInventario creado
        Raises:
            ValueError: Si no hay suficiente inventario disponible
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if verificar_disponibilidad and cantidad > self.cantidad_disponible():
            raise ValueError(
                f"No hay suficiente inventario disponible. "
                f"Disponible: {self.cantidad_disponible()}, Solicitado: {cantidad}"
            )
        
        movimiento = MovimientoInventario(
            tipo=TipoMovimiento.SALIDA,
            cantidad=cantidad,
            motivo=motivo,
            usuario_id=usuario_id
        )
        
        self.cantidad_actual -= cantidad
        self.fecha_actualizacion = datetime.now()
        self._movimientos.append(movimiento)
        
        return movimiento

    def reservar(self, cantidad: int) -> None:
        """
        Reserva una cantidad de inventario
        Args:
            cantidad: Cantidad a reservar
        Raises:
            ValueError: Si no hay suficiente inventario disponible
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if cantidad > self.cantidad_disponible():
            raise ValueError(
                f"No hay suficiente inventario para reservar. "
                f"Disponible: {self.cantidad_disponible()}, Solicitado: {cantidad}"
            )
        
        self.cantidad_reservada += cantidad
        self.fecha_actualizacion = datetime.now()

    def liberar_reserva(self, cantidad: int) -> None:
        """
        Libera una cantidad reservada
        Args:
            cantidad: Cantidad a liberar
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        if cantidad > self.cantidad_reservada:
            raise ValueError(
                f"No se puede liberar más de lo reservado. "
                f"Reservado: {self.cantidad_reservada}, Solicitado: {cantidad}"
            )
        
        self.cantidad_reservada -= cantidad
        self.fecha_actualizacion = datetime.now()

    def ajustar_inventario(
        self,
        nueva_cantidad: int,
        motivo: str,
        usuario_id: int
    ) -> MovimientoInventario:
        """
        Ajusta el inventario a una cantidad específica
        Args:
            nueva_cantidad: Nueva cantidad total
            motivo: Motivo del ajuste
            usuario_id: ID del usuario que registra
        Returns:
            MovimientoInventario creado
        """
        if nueva_cantidad < 0:
            raise ValueError("La nueva cantidad no puede ser negativa")
        
        diferencia = nueva_cantidad - self.cantidad_actual
        
        movimiento = MovimientoInventario(
            tipo=TipoMovimiento.AJUSTE,
            cantidad=abs(diferencia),
            motivo=f"Ajuste: {motivo} (de {self.cantidad_actual} a {nueva_cantidad})",
            usuario_id=usuario_id
        )
        
        self.cantidad_actual = nueva_cantidad
        self.fecha_actualizacion = datetime.now()
        self._movimientos.append(movimiento)
        
        return movimiento

    def __str__(self) -> str:
        return f"Inventario(Producto ID: {self.producto_id}, Disponible: {self.cantidad_disponible()})"

    def __repr__(self) -> str:
        return (
            f"Inventario(id={self.id}, producto_id={self.producto_id}, "
            f"cantidad_actual={self.cantidad_actual}, "
            f"cantidad_reservada={self.cantidad_reservada})"
        )
