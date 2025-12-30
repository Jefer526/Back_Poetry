"""
Admin para gestión de Usuarios - SIN EMPRESA
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.auth import get_user_model

Usuario = get_user_model()


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin personalizado para Usuario"""
    
    list_display = (
        'username',
        'email',
        'nombre_completo',
        'tipo_formatted',
        'activo_formatted',
        'date_joined'
    )
    
    list_filter = (
        'tipo',
        'activo',
        'is_staff',
        'is_superuser',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Tipo y Permisos', {
            'fields': ('tipo', 'activo'),
            'description': 'Tipo de usuario: Administrador (CRUD) o Externo (solo lectura)'
        }),
        ('Permisos Avanzados', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('date_joined', 'last_login', 'fecha_ultimo_acceso'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'fields': (
                'username',
                'password1',
                'password2',
                'email',
                'first_name',
                'last_name',
                'tipo',
                'activo'
            ),
            'description': 'Complete la información del nuevo usuario'
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'fecha_ultimo_acceso')
    
    list_per_page = 25
    
    # Acciones personalizadas
    actions = ['activar_usuarios', 'desactivar_usuarios']
    
    def tipo_formatted(self, obj):
        """Tipo de usuario con colores"""
        if obj.tipo == 'administrador':
            return format_html(
                '<span style="color: white; background-color: #417690; padding: 3px 10px; border-radius: 3px; font-weight: bold;">👤 ADMIN</span>'
            )
        return format_html(
            '<span style="color: white; background-color: #6c757d; padding: 3px 10px; border-radius: 3px;">👥 EXTERNO</span>'
        )
    tipo_formatted.short_description = 'Tipo'
    tipo_formatted.admin_order_field = 'tipo'
    
    def activo_formatted(self, obj):
        """Estado activo con colores"""
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
        )
    activo_formatted.short_description = 'Estado'
    activo_formatted.admin_order_field = 'activo'
    
    @admin.action(description='✓ Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        """Activar usuarios en masa"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'✓ {count} usuario(s) activado(s) exitosamente',
            level='success'
        )
    
    @admin.action(description='✗ Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        """Desactivar usuarios en masa"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'✓ {count} usuario(s) desactivado(s) exitosamente',
            level='success'
        )