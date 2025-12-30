"""
Admin para Chatbot (IA)
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ConversacionChatbot, MensajeChatbot


class MensajeChatbotInline(admin.TabularInline):
    """Inline para ver mensajes de una conversación"""
    model = MensajeChatbot
    extra = 0
    readonly_fields = ('rol', 'contenido', 'timestamp')
    can_delete = False
    max_num = 20
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ConversacionChatbot)
class ConversacionChatbotAdmin(admin.ModelAdmin):
    """Admin para conversaciones del chatbot"""
    
    list_display = (
        'id',
        'usuario',
        'titulo_corto',
        'total_mensajes',
        'activa_formatted',
        'created_at',
        'updated_at'
    )
    
    list_filter = (
        'activa',
        'created_at',
        'usuario'
    )
    
    search_fields = (
        'titulo',
        'usuario__username',
        'mensajes__contenido'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Conversación', {
            'fields': ('usuario', 'titulo', 'activa')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MensajeChatbotInline]
    
    list_per_page = 25
    
    def titulo_corto(self, obj):
        if obj.titulo:
            return obj.titulo[:50] + '...' if len(obj.titulo) > 50 else obj.titulo
        return '-'
    titulo_corto.short_description = 'Título'
    
    def total_mensajes(self, obj):
        count = obj.mensajes.count()
        return format_html(
            '<span style="font-weight: bold; color: blue;">{}</span>',
            count
        )
    total_mensajes.short_description = 'Mensajes'
    
    def activa_formatted(self, obj):
        if obj.activa:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activa</span>'
            )
        return format_html(
            '<span style="color: gray;">✗ Archivada</span>'
        )
    activa_formatted.short_description = 'Estado'


@admin.register(MensajeChatbot)
class MensajeChatbotAdmin(admin.ModelAdmin):
    """Admin para mensajes del chatbot"""
    
    list_display = (
        'id',
        'conversacion_id',
        'conversacion_usuario',
        'rol_formatted',
        'contenido_corto',
        'timestamp'
    )
    
    list_filter = (
        'rol',
        'timestamp'
    )
    
    search_fields = (
        'contenido',
        'conversacion__titulo',
        'conversacion__usuario__username'
    )
    
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Mensaje', {
            'fields': ('conversacion', 'rol', 'contenido')
        }),
        ('Fecha', {
            'fields': ('timestamp',)
        }),
    )
    
    list_per_page = 50
    
    def conversacion_usuario(self, obj):
        return obj.conversacion.usuario.username
    conversacion_usuario.short_description = 'Usuario'
    conversacion_usuario.admin_order_field = 'conversacion__usuario__username'
    
    def rol_formatted(self, obj):
        if obj.rol == 'user':
            return format_html(
                '<span style="color: blue; font-weight: bold;">👤 Usuario</span>'
            )
        elif obj.rol == 'assistant':
            return format_html(
                '<span style="color: green; font-weight: bold;">🤖 Asistente</span>'
            )
        return obj.get_rol_display()
    rol_formatted.short_description = 'Rol'
    
    def contenido_corto(self, obj):
        return obj.contenido[:100] + '...' if len(obj.contenido) > 100 else obj.contenido
    contenido_corto.short_description = 'Contenido'
