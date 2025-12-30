"""
Serializers para la API REST de Empresas
Siguiendo el principio de especialización (diferentes serializers para diferentes casos de uso)
"""
from rest_framework import serializers
from .models import Empresa


class EmpresaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar empresas (solo campos necesarios)
    Optimizado para reducir transferencia de datos
    """
    class Meta:
        model = Empresa
        fields = [
            'id',
            'nit',
            'nombre',
            'email',
            'activa',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmpresaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para ver detalle completo de una empresa
    Incluye todos los campos
    """
    class Meta:
        model = Empresa
        fields = [
            'id',
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmpresaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear una nueva empresa
    Validaciones específicas para creación
    """
    class Meta:
        model = Empresa
        fields = [
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa'
        ]
    
    def validate_nit(self, value):
        """
        Validación personalizada para el NIT
        """
        # Limpiar espacios
        value = value.strip()
        
        # Validar longitud
        if len(value) < 9 or len(value) > 15:
            raise serializers.ValidationError(
                "El NIT debe tener entre 9 y 15 caracteres"
            )
        
        return value
    
    def validate_email(self, value):
        """
        Validación personalizada para el email
        """
        value = value.lower().strip()
        
        # Verificar si ya existe (excepto para la misma empresa en actualización)
        if self.instance:
            if Empresa.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError(
                    "Ya existe una empresa con este email"
                )
        else:
            if Empresa.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Ya existe una empresa con este email"
                )
        
        return value
    
    def create(self, validated_data):
        """
        Crear empresa usando validaciones del dominio
        """
        try:
            empresa = Empresa(**validated_data)
            empresa.full_clean()  # Validaciones de Django
            empresa.save()  # Validaciones de dominio en el save()
            return empresa
        except Exception as e:
            raise serializers.ValidationError(str(e))


class EmpresaUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar una empresa existente
    Permite actualización parcial
    """
    class Meta:
        model = Empresa
        fields = [
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa'
        ]
    
    def validate_email(self, value):
        """
        Validación de email único para actualización
        """
        value = value.lower().strip()
        
        if Empresa.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "Ya existe una empresa con este email"
            )
        
        return value
    
    def update(self, instance, validated_data):
        """
        Actualizar empresa usando validaciones del dominio
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.full_clean()
            instance.save()
            return instance
        except Exception as e:
            raise serializers.ValidationError(str(e))


class EmpresaSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para cuando se necesita referenciar una empresa
    desde otros modelos (ej: en Producto)
    """
    class Meta:
        model = Empresa
        fields = ['id', 'nit', 'nombre']
        read_only_fields = ['id', 'nit', 'nombre']
