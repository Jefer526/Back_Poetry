"""
Admin de Inventario - CON PDF Y EMAIL
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Inventario, MovimientoInventario
from .reports import generar_pdf_inventario, generar_pdf_movimientos
from datetime import datetime


class MovimientoInventarioInline(admin.TabularInline):
    """Inline para ver últimos movimientos"""
    model = MovimientoInventario
    extra = 0
    readonly_fields = ('tipo', 'cantidad', 'motivo', 'usuario', 'fecha')
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    """Admin para Inventario con PDF y Email"""
    
    list_display = (
        'producto_codigo',
        'producto_nombre',
        'cantidad_actual_formatted',
        'ubicacion',
        'estado_stock',
        'updated_at'
    )
    
    list_filter = (
        'producto__tipo',
        'producto__empresa',
        'updated_at'
    )
    
    search_fields = (
        'producto__codigo',
        'producto__nombre',
        'ubicacion',
    )
    
    ordering = ('-updated_at',)
    
    readonly_fields = (
        'producto',
        'cantidad_actual',
        'estado_stock_detail',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('Producto', {
            'fields': ('producto',),
            'description': '⚠️ Para cambiar el stock, usa "Movimientos de Inventario" en el menú lateral'
        }),
        ('Stock (Solo Lectura)', {
            'fields': (
                'cantidad_actual',
                'estado_stock_detail'
            ),
        }),
        ('Ubicación', {
            'fields': ('ubicacion',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MovimientoInventarioInline]
    list_per_page = 25
    
    # ACCIONES PERSONALIZADAS
    actions = [
        'descargar_pdf_inventario',
        'enviar_pdf_por_email',
        'reporte_stock_bajo',
    ]
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.movimientos.exists():
            return False
        return True
    
    def producto_codigo(self, obj):
        return obj.producto.codigo
    producto_codigo.short_description = 'Código'
    producto_codigo.admin_order_field = 'producto__codigo'
    
    def producto_nombre(self, obj):
        return obj.producto.nombre
    producto_nombre.short_description = 'Producto'
    producto_nombre.admin_order_field = 'producto__nombre'
    
    def cantidad_actual_formatted(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            obj.cantidad_actual
        )
    cantidad_actual_formatted.short_description = 'Stock'
    cantidad_actual_formatted.admin_order_field = 'cantidad_actual'
    
    def estado_stock(self, obj):
        cantidad = obj.cantidad_actual
        
        if cantidad <= 0:
            return format_html(
                '<span style="color: white; background-color: red; padding: 3px 8px; border-radius: 3px;">⚠ SIN STOCK</span>'
            )
        elif cantidad <= obj.producto.stock_minimo:
            return format_html(
                '<span style="color: white; background-color: orange; padding: 3px 8px; border-radius: 3px;">⚡ BAJO</span>'
            )
        else:
            return format_html(
                '<span style="color: white; background-color: green; padding: 3px 8px; border-radius: 3px;">✓ OK</span>'
            )
    estado_stock.short_description = 'Estado'
    
    def estado_stock_detail(self, obj):
        cantidad = obj.cantidad_actual
        stock_min = obj.producto.stock_minimo
        
        if cantidad <= 0:
            mensaje = f"⚠️ SIN STOCK - Reabastecer urgentemente"
            color = "red"
        elif cantidad <= stock_min:
            mensaje = f"⚡ STOCK BAJO - Stock: {cantidad} / Mínimo: {stock_min}"
            color = "orange"
        else:
            mensaje = f"✓ STOCK OK - Stock: {cantidad} / Mínimo: {stock_min}"
            color = "green"
        
        return format_html(
            '<div style="padding: 10px; background-color: {}; color: white; border-radius: 5px; font-weight: bold;">{}</div>',
            color,
            mensaje
        )
    estado_stock_detail.short_description = 'Estado del Stock'
    
    # ========================================
    # ACCIÓN: DESCARGAR PDF
    # ========================================
    @admin.action(description='📄 Descargar PDF de inventarios seleccionados')
    def descargar_pdf_inventario(self, request, queryset):
        """Genera y descarga PDF de los inventarios seleccionados"""
        try:
            # Generar PDF
            pdf_buffer = generar_pdf_inventario(
                queryset,
                titulo=f"Reporte de Inventario - {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            # Crear respuesta HTTP
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            filename = f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            self.message_user(request, f'✓ PDF generado exitosamente: {queryset.count()} producto(s)')
            return response
            
        except Exception as e:
            self.message_user(request, f'❌ Error al generar PDF: {str(e)}', level='error')
    
    # ========================================
    # ACCIÓN: ENVIAR PDF POR EMAIL
    # ========================================
    @admin.action(description='📧 Enviar PDF por correo electrónico')
    def enviar_pdf_por_email(self, request, queryset):
        """Genera PDF y lo envía por email"""
        try:
            # Generar PDF
            pdf_buffer = generar_pdf_inventario(
                queryset,
                titulo=f"Reporte de Inventario - {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            # Preparar email
            destinatario = request.user.email if request.user.email else settings.DEFAULT_FROM_EMAIL
            
            email = EmailMessage(
                subject=f'Reporte de Inventario - {datetime.now().strftime("%d/%m/%Y")}',
                body=f'Adjunto encontrará el reporte de inventario solicitado.\n\n'
                     f'Total de productos: {queryset.count()}\n'
                     f'Generado por: {request.user.username}\n'
                     f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            
            # Adjuntar PDF
            filename = f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            email.attach(filename, pdf_buffer.read(), 'application/pdf')
            
            # Enviar
            email.send()
            
            self.message_user(
                request,
                f'✓ Email enviado exitosamente a: {destinatario}',
                level='success'
            )
            
        except Exception as e:
            self.message_user(
                request,
                f'❌ Error al enviar email: {str(e)}',
                level='error'
            )
    
    # ========================================
    # ACCIÓN: REPORTE DE STOCK BAJO
    # ========================================
    @admin.action(description='📊 Reporte de productos con stock bajo')
    def reporte_stock_bajo(self, request, queryset):
        """Genera reporte de productos con stock bajo"""
        bajo_stock = [
            inv for inv in queryset 
            if inv.cantidad_actual <= inv.producto.stock_minimo
        ]
        
        if not bajo_stock:
            self.message_user(
                request,
                '✓ Todos los productos seleccionados tienen stock adecuado',
                level='success'
            )
            return
        
        # Generar PDF solo de productos con stock bajo
        try:
            pdf_buffer = generar_pdf_inventario(
                bajo_stock,
                titulo=f"Alerta: Productos con Stock Bajo - {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            filename = f"stock_bajo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            self.message_user(
                request,
                f'⚠️ {len(bajo_stock)} producto(s) con stock bajo. PDF generado.',
                level='warning'
            )
            return response
            
        except Exception as e:
            self.message_user(request, f'❌ Error: {str(e)}', level='error')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """Admin para Movimientos con PDF"""
    
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
    readonly_fields = ('usuario', 'fecha')
    
    fieldsets = (
        ('Movimiento', {
            'fields': ('inventario', 'tipo', 'cantidad', 'motivo'),
            'description': 'ENTRADA: Agrega al stock | SALIDA: Resta del stock'
        }),
        ('Auditoría', {
            'fields': ('usuario', 'fecha'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 50
    
    # ACCIONES
    actions = ['descargar_pdf_movimientos']
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def save_model(self, request, obj, form, change):
        """Guardar movimiento y actualizar inventario"""
        if not obj.usuario:
            obj.usuario = request.user
        
        super().save_model(request, obj, form, change)
        
        if not change:
            inventario = obj.inventario
            
            if obj.tipo == 'entrada':
                inventario.cantidad_actual += obj.cantidad
                inventario.save()
                self.message_user(
                    request,
                    f'✓ Entrada: +{obj.cantidad} unidades. Nuevo stock: {inventario.cantidad_actual}',
                    level='success'
                )
            elif obj.tipo == 'salida':
                if inventario.cantidad_actual >= obj.cantidad:
                    inventario.cantidad_actual -= obj.cantidad
                    inventario.save()
                    self.message_user(
                        request,
                        f'✓ Salida: -{obj.cantidad} unidades. Nuevo stock: {inventario.cantidad_actual}',
                        level='success'
                    )
                else:
                    obj.delete()
                    self.message_user(
                        request,
                        f'❌ Stock insuficiente. Actual: {inventario.cantidad_actual}, Solicitado: {obj.cantidad}',
                        level='error'
                    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Limitar opciones de tipo"""
        form = super().get_form(request, obj, **kwargs)
        if 'tipo' in form.base_fields:
            form.base_fields['tipo'].choices = [
                ('entrada', 'Entrada'),
                ('salida', 'Salida'),
            ]
        return form
    
    def inventario_producto(self, obj):
        return obj.inventario.producto.codigo
    inventario_producto.short_description = 'Producto'
    inventario_producto.admin_order_field = 'inventario__producto__codigo'
    
    def tipo_formatted(self, obj):
        if obj.tipo == 'entrada':
            return format_html(
                '<span style="color: green; font-weight: bold;">↑ ENTRADA</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">↓ SALIDA</span>'
        )
    tipo_formatted.short_description = 'Tipo'
    
    def motivo_short(self, obj):
        if obj.motivo:
            return obj.motivo[:50] + '...' if len(obj.motivo) > 50 else obj.motivo
        return '-'
    motivo_short.short_description = 'Motivo'
    
    # ========================================
    # ACCIÓN: DESCARGAR PDF DE MOVIMIENTOS
    # ========================================
    @admin.action(description='📄 Descargar PDF de movimientos seleccionados')
    def descargar_pdf_movimientos(self, request, queryset):
        """Genera PDF de movimientos"""
        try:
            pdf_buffer = generar_pdf_movimientos(
                queryset,
                titulo=f"Reporte de Movimientos - {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            filename = f"movimientos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            self.message_user(request, f'✓ PDF generado: {queryset.count()} movimiento(s)')
            return response
            
        except Exception as e:
            self.message_user(request, f'❌ Error: {str(e)}', level='error')