"""
Views para Chatbot (IA)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ConversacionChatbot, MensajeChatbot
from .serializers import (
    ConversacionChatbotSerializer,
    ConversacionListSerializer,
    MensajeChatbotSerializer,
    ChatbotMensajeInputSerializer
)
from .services import ServicioChatbot


class ChatbotViewSet(viewsets.ViewSet):
    """
    ViewSet para chatbot conversacional (IA)
    
    Endpoints:
    - POST   /api/ia/mensaje/                  - Enviar mensaje al chatbot
    - GET    /api/ia/conversaciones/           - Listar mis conversaciones
    - GET    /api/ia/conversaciones/{id}/      - Ver conversación específica
    - DELETE /api/ia/conversaciones/{id}/      - Eliminar conversación
    - POST   /api/ia/nueva-conversacion/       - Crear nueva conversación
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio_chatbot = ServicioChatbot()
    
    @action(detail=False, methods=['post'])
    def mensaje(self, request):
        """
        Enviar mensaje al chatbot
        
        POST /api/ia/mensaje/
        Body: {
            "mensaje": "¿Cuántos productos tengo en stock?",
            "conversacion_id": 1,  // opcional
            "incluir_contexto": true
        }
        """
        serializer = ChatbotMensajeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mensaje_usuario = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        incluir_contexto = serializer.validated_data.get('incluir_contexto', True)
        
        # Obtener o crear conversación
        if conversacion_id:
            conversacion = get_object_or_404(
                ConversacionChatbot,
                id=conversacion_id,
                usuario=request.user
            )
        else:
            # Crear nueva conversación
            # Título: primeras 50 caracteres del mensaje
            titulo = mensaje_usuario[:50]
            conversacion = ConversacionChatbot.objects.create(
                usuario=request.user,
                titulo=titulo
            )
        
        # Guardar mensaje del usuario
        mensaje_user = MensajeChatbot.objects.create(
            conversacion=conversacion,
            rol='user',
            contenido=mensaje_usuario
        )
        
        # Obtener historial (excluyendo el mensaje actual)
        historial_previo = conversacion.mensajes.exclude(
            id=mensaje_user.id
        ).order_by('timestamp').values('rol', 'contenido')
        
        historial = [
            {"role": msg['rol'], "content": msg['contenido']}
            for msg in historial_previo
        ]
        
        # Generar contexto del sistema si se solicita
        contexto_sistema = None
        if incluir_contexto:
            contexto_sistema = self._generar_contexto_sistema(request.user)
        
        # Generar respuesta del chatbot
        respuesta = self.servicio_chatbot.generar_respuesta(
            mensaje_usuario,
            historial=historial,
            contexto_sistema=contexto_sistema
        )
        
        # Guardar respuesta del asistente
        mensaje_assistant = MensajeChatbot.objects.create(
            conversacion=conversacion,
            rol='assistant',
            contenido=respuesta
        )
        
        return Response({
            'conversacion_id': conversacion.id,
            'titulo': conversacion.titulo,
            'mensaje_usuario': MensajeChatbotSerializer(mensaje_user).data,
            'respuesta': MensajeChatbotSerializer(mensaje_assistant).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def conversaciones(self, request):
        """
        Listar conversaciones del usuario
        
        GET /api/ia/conversaciones/
        """
        conversaciones = ConversacionChatbot.objects.filter(
            usuario=request.user
        ).prefetch_related('mensajes').order_by('-updated_at')
        
        serializer = ConversacionListSerializer(conversaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conversacion(self, request, pk=None):
        """
        Ver conversación específica con todos los mensajes
        
        GET /api/ia/conversaciones/{id}/
        """
        conversacion = get_object_or_404(
            ConversacionChatbot,
            id=pk,
            usuario=request.user
        )
        
        serializer = ConversacionChatbotSerializer(conversacion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def eliminar_conversacion(self, request, pk=None):
        """
        Eliminar conversación
        
        DELETE /api/ia/conversaciones/{id}/
        """
        conversacion = get_object_or_404(
            ConversacionChatbot,
            id=pk,
            usuario=request.user
        )
        
        conversacion.delete()
        return Response(
            {'message': 'Conversación eliminada exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def nueva_conversacion(self, request):
        """
        Crear nueva conversación vacía
        
        POST /api/ia/nueva-conversacion/
        Body: {
            "titulo": "Mi nueva conversación"  // opcional
        }
        """
        titulo = request.data.get('titulo', 'Nueva conversación')
        
        conversacion = ConversacionChatbot.objects.create(
            usuario=request.user,
            titulo=titulo
        )
        
        serializer = ConversacionChatbotSerializer(conversacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generar_contexto_sistema(self, usuario):
        """Genera contexto del sistema para el chatbot"""
        from backend.apps.productos.models import Producto
        from backend.apps.empresas.models import Empresa
        from backend.apps.inventario.models import Inventario
        from django.db.models import F
        
        # Estadísticas básicas
        total_productos = Producto.objects.count()
        total_empresas = Empresa.objects.count()
        
        # Productos con bajo stock
        bajo_stock = Inventario.objects.filter(
            cantidad_actual__lte=F('producto__stock_minimo')
        ).count()
        
        # Stock total
        total_stock = sum(inv.cantidad_actual for inv in Inventario.objects.all())
        
        contexto = f"""Sistema Lite Thinking - Estado Actual:

📊 Estadísticas Generales:
- Empresas registradas: {total_empresas}
- Productos totales: {total_productos}
- Stock total en sistema: {total_stock} unidades
- Productos con stock bajo: {bajo_stock}

👤 Usuario Actual:
- Nombre: {usuario.username}
- Tipo: {usuario.get_tipo_display()}
- Permisos: {'CRUD completo' if usuario.es_administrador else 'Solo lectura'}

Esta información te ayuda a responder preguntas sobre el estado actual del sistema."""
        
        return contexto
