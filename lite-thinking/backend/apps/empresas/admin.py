"""
Configuración del Django Admin para Empresas
"""
from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Empresa
    """
    # Campos a mostrar en la lista
    list_display = (
        'nit',
        'nombre',
        'telefono',
        'email',
        'activa',
        'created_at'
    )
    
    # Filtros laterales
    list_filter = (
        'activa',
        'created_at',
        'updated_at'
    )
    
    # Campos de búsqueda
    search_fields = (
        'nit',
        'nombre',
        'email',
        'telefono'
    )
    
    # Ordenamiento por defecto
    ordering = ('-created_at',)
    
    # Campos de solo lectura
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nit', 'nombre')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos que se pueden editar directamente en la lista
    list_editable = ('activa',)
    
    # Número de items por página
    list_per_page = 20
    
    # Agregar acciones personalizadas
    actions = ['activar_empresas', 'desactivar_empresas']
    
    @admin.action(description='Activar empresas seleccionadas')
    def activar_empresas(self, request, queryset):
        """Activa las empresas seleccionadas"""
        updated = queryset.update(activa=True)
        self.message_user(
            request,
            f'{updated} empresa(s) activada(s) exitosamente.'
        )
    
    @admin.action(description='Desactivar empresas seleccionadas')
    def desactivar_empresas(self, request, queryset):
        """Desactiva las empresas seleccionadas"""
        updated = queryset.update(activa=False)
        self.message_user(
            request,
            f'{updated} empresa(s) desactivada(s) exitosamente.'
        )
