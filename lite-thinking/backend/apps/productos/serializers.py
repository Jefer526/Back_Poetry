"""
Serializers para la API REST de Productos
Siguiendo el principio de especialización (diferentes serializers para diferentes casos de uso)
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Producto
from backend.apps.empresas.serializers import EmpresaSimpleSerializer


class ProductoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar productos (optimizado)
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'empresa',
            'empresa_nombre',
            'precio_usd',
            'tipo',
            'tipo_display',
            'activo',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para ver detalle completo de un producto
    """
    empresa_detalle = EmpresaSimpleSerializer(source='empresa', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    precio_cop = serializers.SerializerMethodField()
    precio_eur = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'empresa',
            'empresa_detalle',
            'codigo',
            'nombre',
            'descripcion',
            'precio_usd',
            'precio_cop',
            'precio_eur',
            'tipo',
            'tipo_display',
            'activo',
            'stock_minimo',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_precio_cop(self, obj):
        """Calcula precio en COP (tasa 1 USD = 4000 COP)"""
        try:
            tasa = self.context.get('tasa_cop', Decimal('4000'))
            return float(obj.calcular_precio_cop(tasa))
        except:
            return None
    
    def get_precio_eur(self, obj):
        """Calcula precio en EUR (tasa 1 USD = 0.92 EUR)"""
        try:
            tasa = self.context.get('tasa_eur', Decimal('0.92'))
            return float(obj.calcular_precio_eur(tasa))
        except:
            return None


class ProductoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear un nuevo producto
    """
    class Meta:
        model = Producto
        fields = [
            'empresa',
            'codigo',
            'nombre',
            'descripcion',
            'precio_usd',
            'tipo',
            'activo',
            'stock_minimo'
        ]
    
    def validate_codigo(self, value):
        """Validación personalizada para el código"""
        value = value.strip().upper()
        
        if len(value) > 50:
            raise serializers.ValidationError(
                "El código no puede exceder 50 caracteres"
            )
        
        return value
    
    def validate_precio_usd(self, value):
        """Validación personalizada para el precio"""
        if value <= 0:
            raise serializers.ValidationError(
                "El precio debe ser mayor a 0"
            )
        
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError(
                "El precio excede el límite permitido"
            )
        
        return value
    
    def validate_stock_minimo(self, value):
        """Validación personalizada para stock mínimo"""
        if value < 0:
            raise serializers.ValidationError(
                "El stock mínimo no puede ser negativo"
            )
        
        return value
    
    def create(self, validated_data):
        """Crear producto usando validaciones del dominio"""
        try:
            producto = Producto(**validated_data)
            producto.full_clean()
            producto.save()
            return producto
        except Exception as e:
            raise serializers.ValidationError(str(e))


class ProductoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar un producto existente
    """
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'precio_usd',
            'tipo',
            'activo',
            'stock_minimo'
        ]
    
    def validate_precio_usd(self, value):
        """Validación de precio para actualización"""
        if value <= 0:
            raise serializers.ValidationError(
                "El precio debe ser mayor a 0"
            )
        
        return value
    
    def update(self, instance, validated_data):
        """Actualizar producto usando validaciones del dominio"""
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.full_clean()
            instance.save()
            return instance
        except Exception as e:
            raise serializers.ValidationError(str(e))


class ProductoSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para cuando se necesita referenciar un producto
    desde otros modelos (ej: en Inventario)
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'empresa',
            'empresa_nombre',
            'precio_usd'
        ]
        read_only_fields = fields


class ProductoPreciosSerializer(serializers.ModelSerializer):
    """
    Serializer especializado para operaciones con precios multi-moneda
    """
    precio_cop = serializers.SerializerMethodField()
    precio_eur = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'precio_usd',
            'precio_cop',
            'precio_eur'
        ]
    
    def get_precio_cop(self, obj):
        """Precio en COP"""
        tasa = self.context.get('tasa_cop', Decimal('4000'))
        return float(obj.calcular_precio_cop(tasa))
    
    def get_precio_eur(self, obj):
        """Precio en EUR"""
        tasa = self.context.get('tasa_eur', Decimal('0.92'))
        return float(obj.calcular_precio_eur(tasa))
