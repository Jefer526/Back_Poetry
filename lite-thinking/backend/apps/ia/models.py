"""
Modelos Django para Chatbot (IA)
Mapeo con entidades de dominio
"""
from django.db import models
from django.conf import settings
from dominio.entidades.conversacion import (
    Conversacion as ConversacionDominio,
    Mensaje as MensajeDominio,
    RolMensaje
)


class ConversacionChatbot(models.Model):
    """
    Modelo Django para Conversación
    Se mapea con la entidad de dominio Conversacion
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversaciones',
        verbose_name="Usuario"
    )
    
    titulo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título generado automáticamente del primer mensaje"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name="Conversación Activa"
    )
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ['-updated_at']
        db_table = 'conversaciones_chatbot'
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo or 'Nueva conversación'}"
    
    # ========================================
    # MAPEO CON ENTIDAD DE DOMINIO
    # ========================================
    
    def to_domain(self) -> ConversacionDominio:
        """Convierte el modelo Django a entidad de dominio"""
        # Obtener mensajes y convertirlos
        mensajes_django = self.mensajes.all().order_by('timestamp')
        mensajes_dominio = [
            MensajeDominio(
                id=msg.id,
                rol=RolMensaje(msg.rol),
                contenido=msg.contenido,
                timestamp=msg.timestamp
            )
            for msg in mensajes_django
        ]
        
        return ConversacionDominio(
            id=self.id,
            usuario_id=self.usuario_id,
            titulo=self.titulo,
            activa=self.activa,
            created_at=self.created_at,
            updated_at=self.updated_at,
            mensajes=mensajes_dominio
        )
    
    @classmethod
    def from_domain(cls, entidad: ConversacionDominio, usuario):
        """Crea/actualiza modelo Django desde entidad de dominio"""
        return cls(
            id=entidad.id,
            usuario=usuario,
            titulo=entidad.titulo,
            activa=entidad.activa,
            created_at=entidad.created_at,
            updated_at=entidad.updated_at
        )


class MensajeChatbot(models.Model):
    """
    Modelo Django para Mensaje
    Se mapea con la entidad de dominio Mensaje
    """
    ROL_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
    ]
    
    conversacion = models.ForeignKey(
        ConversacionChatbot,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name="Conversación"
    )
    
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        verbose_name="Rol"
    )
    
    contenido = models.TextField(
        verbose_name="Contenido del Mensaje"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['timestamp']
        db_table = 'mensajes_chatbot'
        indexes = [
            models.Index(fields=['conversacion', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_rol_display()}: {self.contenido[:50]}..."
    
    # ========================================
    # MAPEO CON ENTIDAD DE DOMINIO
    # ========================================
    
    def to_domain(self) -> MensajeDominio:
        """Convierte el modelo Django a entidad de dominio"""
        return MensajeDominio(
            id=self.id,
            rol=RolMensaje(self.rol),
            contenido=self.contenido,
            timestamp=self.timestamp
        )
    
    @classmethod
    def from_domain(cls, entidad: MensajeDominio, conversacion):
        """Crea/actualiza modelo Django desde entidad de dominio"""
        return cls(
            id=entidad.id,
            conversacion=conversacion,
            rol=entidad.rol.value,
            contenido=entidad.contenido,
            timestamp=entidad.timestamp
        )
