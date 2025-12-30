"""
Entidad Empresa - Dominio Puro
Sin dependencias de Django o frameworks externos
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Empresa:
    """
    Entidad de dominio que representa una Empresa
    Reglas de negocio puras sin lógica de persistencia
    """
    nit: str
    nombre: str
    direccion: str
    telefono: str
    email: str
    activa: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones de dominio al crear la entidad"""
        self.validar()

    def validar(self) -> None:
        """
        Validaciones de reglas de negocio
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.nit or len(self.nit.strip()) == 0:
            raise ValueError("El NIT es obligatorio")
        
        if len(self.nit) < 9 or len(self.nit) > 15:
            raise ValueError("El NIT debe tener entre 9 y 15 caracteres")
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        
        if len(self.nombre) > 200:
            raise ValueError("El nombre no puede exceder 200 caracteres")
        
        if not self.email or '@' not in self.email:
            raise ValueError("Email inválido")
        
        if not self.telefono or len(self.telefono) < 7:
            raise ValueError("Teléfono inválido")

    def activar(self) -> None:
        """Activa la empresa"""
        self.activa = True
        self.fecha_actualizacion = datetime.now()

    def desactivar(self) -> None:
        """Desactiva la empresa"""
        self.activa = False
        self.fecha_actualizacion = datetime.now()

    def actualizar_informacion(
        self,
        nombre: Optional[str] = None,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None
    ) -> None:
        """
        Actualiza la información de la empresa
        Solo actualiza los campos proporcionados
        """
        if nombre is not None:
            self.nombre = nombre
        if direccion is not None:
            self.direccion = direccion
        if telefono is not None:
            self.telefono = telefono
        if email is not None:
            self.email = email
        
        self.fecha_actualizacion = datetime.now()
        self.validar()

    def __str__(self) -> str:
        return f"Empresa({self.nit} - {self.nombre})"

    def __repr__(self) -> str:
        return (
            f"Empresa(id={self.id}, nit='{self.nit}', nombre='{self.nombre}', "
            f"activa={self.activa})"
        )
