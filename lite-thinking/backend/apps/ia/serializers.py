"""
Serializers para Chatbot
"""
from rest_framework import serializers
from .models import ConversacionChatbot, MensajeChatbot


class MensajeChatbotSerializer(serializers.ModelSerializer):
    """Serializer para mensajes del chatbot"""
    
    class Meta:
        model = MensajeChatbot
        fields = [
            'id',
            'rol',
            'contenido',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ConversacionChatbotSerializer(serializers.ModelSerializer):
    """Serializer para conversaciones completas"""
    mensajes = MensajeChatbotSerializer(many=True, read_only=True)
    total_mensajes = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversacionChatbot
        fields = [
            'id',
            'titulo',
            'created_at',
            'updated_at',
            'activa',
            'total_mensajes',
            'mensajes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_mensajes(self, obj):
        return obj.mensajes.count()


class ConversacionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar conversaciones"""
    total_mensajes = serializers.SerializerMethodField()
    ultimo_mensaje = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversacionChatbot
        fields = [
            'id',
            'titulo',
            'created_at',
            'updated_at',
            'activa',
            'total_mensajes',
            'ultimo_mensaje'
        ]
    
    def get_total_mensajes(self, obj):
        return obj.mensajes.count()
    
    def get_ultimo_mensaje(self, obj):
        ultimo = obj.mensajes.last()
        if ultimo:
            return {
                'contenido': ultimo.contenido[:100],
                'rol': ultimo.rol,
                'timestamp': ultimo.timestamp
            }
        return None


class ChatbotMensajeInputSerializer(serializers.Serializer):
    """Serializer para enviar mensaje al chatbot"""
    mensaje = serializers.CharField(
        required=True,
        max_length=2000,
        help_text="Mensaje del usuario al chatbot"
    )
    conversacion_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID de conversación existente (opcional, se crea una nueva si no se proporciona)"
    )
    incluir_contexto = serializers.BooleanField(
        default=True,
        help_text="Incluir contexto del sistema (productos, inventario) en la respuesta"
    )
