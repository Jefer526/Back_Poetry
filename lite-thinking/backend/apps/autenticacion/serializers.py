"""
Serializers para Autenticación JWT - SIN EMPRESA
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer básico para datos del usuario"""
    nombre_completo = serializers.CharField(read_only=True)
    es_administrador = serializers.BooleanField(read_only=True)
    es_externo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nombre_completo',
            'tipo',
            'es_administrador',
            'es_externo',
            'activo',
            'date_joined',
            'fecha_ultimo_acceso'
        ]
        read_only_fields = ['id', 'date_joined', 'fecha_ultimo_acceso']


class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text="Mínimo 8 caracteres"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Debe coincidir con la contraseña"
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'tipo'
        ]
    
    def validate_email(self, value):
        """Validar que el email sea único"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value
    
    def validate_username(self, value):
        """Validar que el username sea único"""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username ya está registrado")
        return value
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Verificar que las contraseñas coincidan
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden"
            })
        
        return data
    
    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario(**validated_data)
        usuario.set_password(password)  # 🔐 Encripta la contraseña
        usuario.save()
        
        return usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para JWT"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar claims personalizados al token
        token['username'] = user.username
        token['email'] = user.email
        token['tipo'] = user.tipo
        token['es_administrador'] = user.es_administrador
        token['es_externo'] = user.es_externo
        
        return token
    
    def validate(self, attrs):
        """Validar credenciales y agregar información del usuario"""
        data = super().validate(attrs)
        
        # Verificar que el usuario esté activo
        if not self.user.activo:
            raise serializers.ValidationError({
                "detail": "Usuario inactivo. Contacte al administrador."
            })
        
        # Agregar información del usuario a la respuesta
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': self.user.nombre_completo,
            'tipo': self.user.tipo,
            'es_administrador': self.user.es_administrador,
            'es_externo': self.user.es_externo,
        }
        
        # Registrar último acceso
        from django.utils import timezone
        self.user.fecha_ultimo_acceso = timezone.now()
        self.user.save(update_fields=['fecha_ultimo_acceso'])
        
        return data


class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    password_actual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_nueva = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_nueva_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_password_actual(self, value):
        """Verificar que la contraseña actual sea correcta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta")
        return value
    
    def validate(self, data):
        """Validar que las contraseñas nuevas coincidan"""
        if data['password_nueva'] != data['password_nueva_confirm']:
            raise serializers.ValidationError({
                "password_nueva": "Las contraseñas nuevas no coinciden"
            })
        return data
    
    def save(self):
        """Cambiar la contraseña"""
        user = self.context['request'].user
        user.set_password(self.validated_data['password_nueva'])
        user.save()
        return user