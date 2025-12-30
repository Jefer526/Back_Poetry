"""
Entidad Usuario - Dominio Puro
Sin dependencias de Django o frameworks externos
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoUsuario(Enum):
    """Tipos de usuario en el sistema"""
    ADMINISTRADOR = "administrador"
    EXTERNO = "externo"


@dataclass
class Usuario:
    """
    Entidad de dominio que representa un Usuario
    Reglas de negocio puras sin lógica de persistencia
    """
    email: str
    nombre: str
    apellido: str
    tipo: TipoUsuario
    activo: bool = True
    empresa_id: Optional[int] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_ultimo_acceso: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        """Validaciones de dominio al crear la entidad"""
        # Convertir string a enum si es necesario
        if isinstance(self.tipo, str):
            self.tipo = TipoUsuario(self.tipo)
        
        self.validar()

    def validar(self) -> None:
        """
        Validaciones de reglas de negocio
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.email or '@' not in self.email:
            raise ValueError("Email inválido")
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        
        if len(self.nombre) > 150:
            raise ValueError("El nombre no puede exceder 150 caracteres")
        
        if not self.apellido or len(self.apellido.strip()) == 0:
            raise ValueError("El apellido es obligatorio")
        
        if len(self.apellido) > 150:
            raise ValueError("El apellido no puede exceder 150 caracteres")
        
        # Usuario externo debe tener empresa asignada
        if self.tipo == TipoUsuario.EXTERNO and not self.empresa_id:
            raise ValueError("Los usuarios externos deben tener una empresa asignada")

    def nombre_completo(self) -> str:
        """
        Retorna el nombre completo del usuario
        Returns:
            Nombre y apellido concatenados
        """
        return f"{self.nombre} {self.apellido}"

    def es_administrador(self) -> bool:
        """
        Verifica si el usuario es administrador
        Returns:
            True si es administrador
        """
        return self.tipo == TipoUsuario.ADMINISTRADOR

    def es_externo(self) -> bool:
        """
        Verifica si el usuario es externo
        Returns:
            True si es externo
        """
        return self.tipo == TipoUsuario.EXTERNO

    def puede_gestionar_empresa(self, empresa_id: int) -> bool:
        """
        Verifica si el usuario puede gestionar una empresa específica
        Args:
            empresa_id: ID de la empresa a verificar
        Returns:
            True si puede gestionar la empresa
        """
        # Administradores pueden gestionar cualquier empresa
        if self.es_administrador():
            return True
        
        # Usuarios externos solo pueden gestionar su empresa asignada
        return self.empresa_id == empresa_id

    def activar(self) -> None:
        """Activa el usuario"""
        self.activo = True

    def desactivar(self) -> None:
        """Desactiva el usuario"""
        self.activo = False

    def registrar_acceso(self) -> None:
        """Registra el último acceso del usuario"""
        self.fecha_ultimo_acceso = datetime.now()

    def cambiar_tipo(self, nuevo_tipo: TipoUsuario, empresa_id: Optional[int] = None) -> None:
        """
        Cambia el tipo de usuario
        Args:
            nuevo_tipo: Nuevo tipo de usuario
            empresa_id: ID de empresa (requerido si cambia a externo)
        Raises:
            ValueError: Si falta empresa_id para usuario externo
        """
        if nuevo_tipo == TipoUsuario.EXTERNO and not empresa_id:
            raise ValueError("Debe especificar una empresa para usuarios externos")
        
        self.tipo = nuevo_tipo
        self.empresa_id = empresa_id

    def __str__(self) -> str:
        return f"Usuario({self.email} - {self.nombre_completo()})"

    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, email='{self.email}', "
            f"nombre='{self.nombre_completo()}', tipo={self.tipo.value}, "
            f"activo={self.activo})"
        )
