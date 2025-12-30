"""
Configuración del Django Admin para Inventario
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Inventario, MovimientoInventario


class MovimientoInventarioInline(admin.TabularInline):
    """Inline para mostrar movimientos dentro del inventario"""
    model = MovimientoInventario
    extra = 0
    readonly_fields = ('tipo', 'cantidad', 'motivo', 'usuario', 'fecha')
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Inventario
    """
    list_display = (
        'producto_codigo',
        'producto_nombre',
        'cantidad_actual_formatted',
        'cantidad_reservada_formatted',
        'cantidad_disponible_formatted',
        'ubicacion',
        'estado_stock',
        'updated_at'
    )
    
    list_filter = (
        'producto__tipo',
        'producto__empresa',
        'created_at',
        'updated_at'
    )
    
    search_fields = (
        'producto__codigo',
        'producto__nombre',
        'ubicacion',
    )
    
    ordering = ('-updated_at',)
    
    readonly_fields = (
        'cantidad_disponible_formatted',
        'estado_stock_detail',
        'created_at',
        'updated_at',
        'historial_movimientos'
    )
    
    autocomplete_fields = ['producto']
    
    fieldsets = (
        ('Producto', {
            'fields': ('producto',)
        }),
        ('Cantidades', {
            'fields': (
                'cantidad_actual',
                'cantidad_reservada',
                'cantidad_disponible_formatted',
                'estado_stock_detail'
            )
        }),
        ('Ubicación', {
            'fields': ('ubicacion',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Historial', {
            'fields': ('historial_movimientos',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MovimientoInventarioInline]
    
    list_per_page = 25
    
    actions = ['generar_reporte_stock', 'alertar_bajo_stock']
    
    def producto_codigo(self, obj):
        """Código del producto"""
        return obj.producto.codigo
    producto_codigo.short_description = 'Código'
    producto_codigo.admin_order_field = 'producto__codigo'
    
    def producto_nombre(self, obj):
        """Nombre del producto"""
        return obj.producto.nombre
    producto_nombre.short_description = 'Producto'
    producto_nombre.admin_order_field = 'producto__nombre'
    
    def cantidad_actual_formatted(self, obj):
        """Formatea la cantidad actual"""
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            obj.cantidad_actual
        )
    cantidad_actual_formatted.short_description = 'Stock Actual'
    cantidad_actual_formatted.admin_order_field = 'cantidad_actual'
    
    def cantidad_reservada_formatted(self, obj):
        """Formatea la cantidad reservada"""
        if obj.cantidad_reservada > 0:
            return format_html(
                '<span style="color: orange;">{}</span>',
                obj.cantidad_reservada
            )
        return obj.cantidad_reservada
    cantidad_reservada_formatted.short_description = 'Reservado'
    cantidad_reservada_formatted.admin_order_field = 'cantidad_reservada'
    
    def cantidad_disponible_formatted(self, obj):
        """Formatea la cantidad disponible"""
        disponible = obj.cantidad_disponible
        
        if disponible <= 0:
            color = 'red'
        elif disponible <= obj.producto.stock_minimo:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            disponible
        )
    cantidad_disponible_formatted.short_description = 'Disponible'
    
    def estado_stock(self, obj):
        """Muestra el estado del stock"""
        disponible = obj.cantidad_disponible
        
        if disponible <= 0:
            return format_html(
                '<span style="color: white; background-color: red; padding: 3px 8px; border-radius: 3px;">⚠ SIN STOCK</span>'
            )
        elif disponible <= obj.producto.stock_minimo:
            return format_html(
                '<span style="color: white; background-color: orange; padding: 3px 8px; border-radius: 3px;">⚡ BAJO</span>'
            )
        else:
            return format_html(
                '<span style="color: white; background-color: green; padding: 3px 8px; border-radius: 3px;">✓ OK</span>'
            )
    estado_stock.short_description = 'Estado'
    
    def estado_stock_detail(self, obj):
        """Detalle del estado del stock para el formulario"""
        disponible = obj.cantidad_disponible
        stock_min = obj.producto.stock_minimo
        
        if disponible <= 0:
            mensaje = f"⚠️ SIN STOCK - Reabastecer urgentemente"
            color = "red"
        elif disponible <= stock_min:
            mensaje = f"⚡ STOCK BAJO - Disponible: {disponible} / Mínimo: {stock_min}"
            color = "orange"
        else:
            mensaje = f"✓ STOCK OK - Disponible: {disponible} / Mínimo: {stock_min}"
            color = "green"
        
        return format_html(
            '<div style="padding: 10px; background-color: {}; color: white; border-radius: 5px; font-weight: bold;">{}</div>',
            color,
            mensaje
        )
    estado_stock_detail.short_description = 'Estado del Stock'
    
    def historial_movimientos(self, obj):
        """Muestra resumen del historial de movimientos"""
        from django.utils.safestring import mark_safe
        
        movimientos = obj.movimientos.all()[:10]
        
        if not movimientos:
            return "No hay movimientos registrados"
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f0f0f0;"><th>Fecha</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th></tr>'
        
        for mov in movimientos:
            tipo_color = {
                'entrada': 'green',
                'salida': 'red',
                'ajuste': 'blue',
                'devolucion': 'orange'
            }.get(mov.tipo, 'black')
            
            html += f'<tr><td>{mov.fecha.strftime("%Y-%m-%d %H:%M")}</td>'
            html += f'<td style="color: {tipo_color}; font-weight: bold;">{mov.get_tipo_display()}</td>'
            html += f'<td>{mov.cantidad}</td>'
            html += f'<td>{mov.motivo or "-"}</td></tr>'
        
        html += '</table>'
        
        return mark_safe(html)
    historial_movimientos.short_description = 'Últimos 10 Movimientos'
    
    @admin.action(description='Generar reporte de stock')
    def generar_reporte_stock(self, request, queryset):
        """Genera un reporte de stock"""
        total_productos = queryset.count()
        total_stock = queryset.aggregate(Sum('cantidad_actual'))['cantidad_actual__sum'] or 0
        
        self.message_user(
            request,
            f'Reporte: {total_productos} productos con {total_stock} unidades en total'
        )
    
    @admin.action(description='Alertar productos con stock bajo')
    def alertar_bajo_stock(self, request, queryset):
        """Muestra productos con stock bajo"""
        bajo_stock = [
            inv for inv in queryset 
            if inv.cantidad_disponible <= inv.producto.stock_minimo
        ]
        
        if bajo_stock:
            productos = ', '.join([inv.producto.codigo for inv in bajo_stock])
            self.message_user(
                request,
                f'⚠️ {len(bajo_stock)} producto(s) con stock bajo: {productos}',
                level='warning'
            )
        else:
            self.message_user(
                request,
                '✓ Todos los productos tienen stock adecuado'
            )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """
    Configuración del admin para MovimientoInventario
    """
    list_display = (
        'fecha',
        'inventario_producto',
        'tipo_formatted',
        'cantidad',
        'motivo_short',
        'usuario'
    )
    
    list_filter = (
        'tipo',
        'fecha',
        'inventario__producto__empresa',
    )
    
    search_fields = (
        'inventario__producto__codigo',
        'inventario__producto__nombre',
        'motivo',
    )
    
    ordering = ('-fecha',)
    
    readonly_fields = (
        'inventario',
        'tipo',
        'cantidad',
        'motivo',
        'usuario',
        'fecha'
    )
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('inventario', 'tipo', 'cantidad')
        }),
        ('Detalles', {
            'fields': ('motivo', 'usuario', 'fecha')
        }),
    )
    
    list_per_page = 50
    
    def has_add_permission(self, request):
        """No permitir agregar movimientos directamente desde el admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar movimientos (auditoría)"""
        return False
    
    def inventario_producto(self, obj):
        """Producto del inventario"""
        return obj.inventario.producto.codigo
    inventario_producto.short_description = 'Producto'
    inventario_producto.admin_order_field = 'inventario__producto__codigo'
    
    def tipo_formatted(self, obj):
        """Formatea el tipo de movimiento con color"""
        colores = {
            'entrada': 'green',
            'salida': 'red',
            'ajuste': 'blue',
            'devolucion': 'orange'
        }
        
        color = colores.get(obj.tipo, 'black')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_formatted.short_description = 'Tipo'
    tipo_formatted.admin_order_field = 'tipo'
    
    def motivo_short(self, obj):
        """Muestra el motivo acortado"""
        if obj.motivo:
            return obj.motivo[:50] + '...' if len(obj.motivo) > 50 else obj.motivo
        return '-'
    motivo_short.short_description = 'Motivo'
