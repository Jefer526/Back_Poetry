"""
Entidad Conversacion - Dominio Puro
Sin dependencias de Django o frameworks externos
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RolMensaje(Enum):
    """Roles de mensajes en el chatbot"""
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Mensaje:
    """
    Entidad de dominio que representa un Mensaje del chatbot
    Reglas de negocio puras sin lógica de persistencia
    """
    rol: RolMensaje
    contenido: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio al crear la entidad"""
        # Convertir string a enum si es necesario
        if isinstance(self.rol, str):
            self.rol = RolMensaje(self.rol)
        
        self.validar()
    
    def validar(self) -> None:
        """
        Validaciones de reglas de negocio
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.contenido or len(self.contenido.strip()) == 0:
            raise ValueError("El contenido del mensaje no puede estar vacío")
        
        if len(self.contenido) > 5000:
            raise ValueError("El mensaje no puede exceder 5000 caracteres")
    
    def es_mensaje_usuario(self) -> bool:
        """Verifica si el mensaje es del usuario"""
        return self.rol == RolMensaje.USER
    
    def es_mensaje_asistente(self) -> bool:
        """Verifica si el mensaje es del asistente"""
        return self.rol == RolMensaje.ASSISTANT
    
    def __str__(self) -> str:
        return f"{self.rol.value}: {self.contenido[:50]}..."
    
    def __repr__(self) -> str:
        return (
            f"Mensaje(id={self.id}, rol={self.rol.value}, "
            f"contenido='{self.contenido[:30]}...', timestamp={self.timestamp})"
        )


@dataclass
class Conversacion:
    """
    Entidad de dominio que representa una Conversación del chatbot
    Reglas de negocio puras sin lógica de persistencia
    """
    usuario_id: int
    titulo: str = ""
    activa: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    mensajes: List[Mensaje] = field(default_factory=list)
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
        if not self.usuario_id or self.usuario_id <= 0:
            raise ValueError("El usuario_id es obligatorio y debe ser positivo")
        
        if self.titulo and len(self.titulo) > 200:
            raise ValueError("El título no puede exceder 200 caracteres")
    
    def agregar_mensaje(self, mensaje: Mensaje) -> None:
        """
        Agrega un mensaje a la conversación
        Args:
            mensaje: Mensaje a agregar
        """
        mensaje.validar()
        self.mensajes.append(mensaje)
        self.updated_at = datetime.now()
    
    def agregar_mensaje_usuario(self, contenido: str) -> Mensaje:
        """
        Crea y agrega un mensaje del usuario
        Args:
            contenido: Contenido del mensaje
        Returns:
            Mensaje creado
        """
        mensaje = Mensaje(
            rol=RolMensaje.USER,
            contenido=contenido
        )
        self.agregar_mensaje(mensaje)
        return mensaje
    
    def agregar_mensaje_asistente(self, contenido: str) -> Mensaje:
        """
        Crea y agrega un mensaje del asistente
        Args:
            contenido: Contenido del mensaje
        Returns:
            Mensaje creado
        """
        mensaje = Mensaje(
            rol=RolMensaje.ASSISTANT,
            contenido=contenido
        )
        self.agregar_mensaje(mensaje)
        return mensaje
    
    def obtener_historial(self) -> List[dict]:
        """
        Obtiene el historial de mensajes en formato para APIs de IA
        Returns:
            Lista de diccionarios con rol y contenido
        """
        return [
            {
                "role": msg.rol.value,
                "content": msg.contenido
            }
            for msg in self.mensajes
        ]
    
    def contar_mensajes(self) -> int:
        """Cuenta el total de mensajes en la conversación"""
        return len(self.mensajes)
    
    def contar_mensajes_usuario(self) -> int:
        """Cuenta mensajes del usuario"""
        return sum(1 for msg in self.mensajes if msg.es_mensaje_usuario())
    
    def contar_mensajes_asistente(self) -> int:
        """Cuenta mensajes del asistente"""
        return sum(1 for msg in self.mensajes if msg.es_mensaje_asistente())
    
    def obtener_ultimo_mensaje(self) -> Optional[Mensaje]:
        """Obtiene el último mensaje de la conversación"""
        return self.mensajes[-1] if self.mensajes else None
    
    def generar_titulo_automatico(self) -> None:
        """
        Genera un título automático basado en el primer mensaje del usuario
        """
        if not self.titulo and self.mensajes:
            primer_mensaje = next(
                (msg for msg in self.mensajes if msg.es_mensaje_usuario()),
                None
            )
            if primer_mensaje:
                # Usar los primeros 50 caracteres del primer mensaje
                self.titulo = primer_mensaje.contenido[:50]
    
    def archivar(self) -> None:
        """Archiva la conversación (la marca como inactiva)"""
        self.activa = False
        self.updated_at = datetime.now()
    
    def reactivar(self) -> None:
        """Reactiva una conversación archivada"""
        self.activa = True
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Conversacion({self.titulo or 'Sin título'} - {self.contar_mensajes()} mensajes)"
    
    def __repr__(self) -> str:
        return (
            f"Conversacion(id={self.id}, usuario_id={self.usuario_id}, "
            f"titulo='{self.titulo}', mensajes={self.contar_mensajes()}, "
            f"activa={self.activa})"
        )
