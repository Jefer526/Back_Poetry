"""
Configuración del Django Admin para Productos
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Producto
    """
    # Campos a mostrar en la lista
    list_display = (
        'codigo',
        'nombre',
        'empresa',
        'precio_usd_formatted',
        'tipo',
        'activo',
        'stock_minimo',
        'created_at'
    )
    
    # Filtros laterales
    list_filter = (
        'activo',
        'tipo',
        'empresa',
        'created_at',
        'updated_at'
    )
    
    # Campos de búsqueda
    search_fields = (
        'codigo',
        'nombre',
        'descripcion',
        'empresa__nombre',
        'empresa__nit'
    )
    
    # Ordenamiento por defecto
    ordering = ('-created_at',)
    
    # Campos de solo lectura
    readonly_fields = (
        'created_at',
        'updated_at',
        'precio_cop_preview',
        'precio_eur_preview',
        'codigo_preview'
    )
    
    # Campos autocompletado
    autocomplete_fields = ['empresa']
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'codigo_preview', 'nombre', 'descripcion', 'empresa'),
            'description': 'Si dejas el código vacío, se generará automáticamente con las 2 primeras letras del nombre.'
        }),
        ('Precios', {
            'fields': ('precio_usd', 'precio_cop_preview', 'precio_eur_preview')
        }),
        ('Clasificación', {
            'fields': ('tipo', 'activo', 'stock_minimo')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos que se pueden editar directamente en la lista
    list_editable = ('activo',)
    
    # Número de items por página
    list_per_page = 25
    
    # Agregar acciones personalizadas
    actions = [
        'activar_productos',
        'desactivar_productos',
    ]
    
    def codigo_preview(self, obj):
        """Muestra información sobre generación de código"""
        if obj and obj.pk:
            return format_html(
                '<span style="color: blue;">✓ Código: <strong>{}</strong></span>',
                obj.codigo
            )
        return format_html(
            '<span style="color: green;">💡 Se generará automáticamente si se deja vacío</span>'
        )
    codigo_preview.short_description = 'Generación Automática'
    
    def precio_usd_formatted(self, obj):
        """Formatea el precio en USD"""
        return format_html(
            '<span style="color: green; font-weight: bold;">${}</span>',
            f'{float(obj.precio_usd):,.2f}'
        )
    precio_usd_formatted.short_description = 'Precio USD'
    
    def precio_cop_preview(self, obj):
        """Muestra precio en COP (tasa ejemplo: 1 USD = 4000 COP)"""
        from decimal import Decimal
        try:
            precio_cop = obj.calcular_precio_cop(Decimal('4000'))
            return f"${float(precio_cop):,.0f} COP (aprox.)"
        except:
            return "N/A"
    precio_cop_preview.short_description = 'Precio COP (referencia)'
    
    def precio_eur_preview(self, obj):
        """Muestra precio en EUR (tasa ejemplo: 1 USD = 0.92 EUR)"""
        from decimal import Decimal
        try:
            precio_eur = obj.calcular_precio_eur(Decimal('0.92'))
            return f"€{float(precio_eur):,.2f} EUR (aprox.)"
        except:
            return "N/A"
    precio_eur_preview.short_description = 'Precio EUR (referencia)'
    
    @admin.action(description='Activar productos seleccionados')
    def activar_productos(self, request, queryset):
        """Activa los productos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(
            request,
            f'{updated} producto(s) activado(s) exitosamente.'
        )
    
    @admin.action(description='Desactivar productos seleccionados')
    def desactivar_productos(self, request, queryset):
        """Desactiva los productos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(
            request,
            f'{updated} producto(s) desactivado(s) exitosamente.'
        )