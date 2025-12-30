"""
Serializers para la API REST de Inventario
"""
from rest_framework import serializers
from .models import Inventario, MovimientoInventario
from backend.apps.productos.serializers import ProductoSimpleSerializer


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """Serializer para MovimientoInventario"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'cantidad',
            'motivo',
            'usuario',
            'usuario_nombre',
            'fecha'
        ]
        read_only_fields = fields
    
    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return None


class InventarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar inventarios"""
    producto_detalle = ProductoSimpleSerializer(source='producto', read_only=True)
    cantidad_disponible = serializers.IntegerField(read_only=True)
    requiere_reabastecimiento = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Inventario
        fields = [
            'id',
            'producto',
            'producto_detalle',
            'cantidad_actual',
            'cantidad_reservada',
            'cantidad_disponible',
            'requiere_reabastecimiento',
            'ubicacion',
            'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class InventarioDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de un inventario"""
    producto_detalle = ProductoSimpleSerializer(source='producto', read_only=True)
    cantidad_disponible = serializers.IntegerField(read_only=True)
    requiere_reabastecimiento = serializers.BooleanField(read_only=True)
    ultimos_movimientos = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventario
        fields = [
            'id',
            'producto',
            'producto_detalle',
            'cantidad_actual',
            'cantidad_reservada',
            'cantidad_disponible',
            'requiere_reabastecimiento',
            'ubicacion',
            'created_at',
            'updated_at',
            'ultimos_movimientos'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_ultimos_movimientos(self, obj):
        """Obtiene los últimos 10 movimientos"""
        movimientos = obj.movimientos.all()[:10]
        return MovimientoInventarioSerializer(movimientos, many=True).data


class InventarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un nuevo inventario"""
    
    class Meta:
        model = Inventario
        fields = [
            'producto',
            'cantidad_actual',
            'cantidad_reservada',
            'ubicacion'
        ]
    
    def validate_producto(self, value):
        """Validar que el producto no tenga ya un inventario"""
        if Inventario.objects.filter(producto=value).exists():
            raise serializers.ValidationError(
                "Este producto ya tiene un inventario registrado"
            )
        return value
    
    def validate_cantidad_actual(self, value):
        """Validar cantidad actual"""
        if value < 0:
            raise serializers.ValidationError(
                "La cantidad actual no puede ser negativa"
            )
        return value
    
    def validate_cantidad_reservada(self, value):
        """Validar cantidad reservada"""
        if value < 0:
            raise serializers.ValidationError(
                "La cantidad reservada no puede ser negativa"
            )
        return value
    
    def validate(self, data):
        """Validación cruzada"""
        if data.get('cantidad_reservada', 0) > data.get('cantidad_actual', 0):
            raise serializers.ValidationError(
                "La cantidad reservada no puede ser mayor que la cantidad actual"
            )
        return data


class InventarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar un inventario"""
    
    class Meta:
        model = Inventario
        fields = [
            'cantidad_actual',
            'cantidad_reservada',
            'ubicacion'
        ]
    
    def validate(self, data):
        """Validación cruzada"""
        cantidad_actual = data.get('cantidad_actual', self.instance.cantidad_actual)
        cantidad_reservada = data.get('cantidad_reservada', self.instance.cantidad_reservada)
        
        if cantidad_reservada > cantidad_actual:
            raise serializers.ValidationError(
                "La cantidad reservada no puede ser mayor que la cantidad actual"
            )
        return data


class MovimientoInventarioCreateSerializer(serializers.Serializer):
    """Serializer para crear movimientos de inventario"""
    inventario_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=['entrada', 'salida', 'ajuste', 'devolucion'])
    cantidad = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField(required=False, allow_blank=True)
    
    def validate_inventario_id(self, value):
        """Validar que el inventario exista"""
        try:
            Inventario.objects.get(id=value)
        except Inventario.DoesNotExist:
            raise serializers.ValidationError("Inventario no encontrado")
        return value
    
    def create(self, validated_data):
        """Crear el movimiento y actualizar el inventario"""
        inventario = Inventario.objects.get(id=validated_data['inventario_id'])
        tipo = validated_data['tipo']
        cantidad = validated_data['cantidad']
        motivo = validated_data.get('motivo', '')
        usuario = self.context.get('request').user if self.context.get('request') else None
        
        # Crear movimiento según el tipo
        if tipo == 'entrada':
            return inventario.registrar_entrada(cantidad, motivo, usuario)
        elif tipo == 'salida':
            return inventario.registrar_salida(cantidad, motivo, usuario)
        elif tipo == 'ajuste':
            return inventario.ajustar_inventario(cantidad, motivo, usuario)
        elif tipo == 'devolucion':
            movimiento = MovimientoInventario.objects.create(
                inventario=inventario,
                tipo='devolucion',
                cantidad=cantidad,
                motivo=motivo,
                usuario=usuario
            )
            inventario.cantidad_actual += cantidad
            inventario.save()
            return movimiento


class ReservaInventarioSerializer(serializers.Serializer):
    """Serializer para reservar/liberar inventario"""
    cantidad = serializers.IntegerField(min_value=1)
    
    def validate_cantidad(self, value):
        """Validar que haya stock disponible"""
        inventario = self.context.get('inventario')
        if inventario and value > inventario.cantidad_disponible:
            raise serializers.ValidationError(
                f"Stock disponible insuficiente. Disponible: {inventario.cantidad_disponible}"
            )
        return value
