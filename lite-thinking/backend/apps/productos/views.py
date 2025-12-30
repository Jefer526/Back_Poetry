"""
Views (API endpoints) para Productos
Usando ViewSets de Django REST Framework
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

from .models import Producto
from .serializers import (
    ProductoListSerializer,
    ProductoDetailSerializer,
    ProductoCreateSerializer,
    ProductoUpdateSerializer,
    ProductoPreciosSerializer
)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Productos
    Proporciona operaciones CRUD completas + endpoints personalizados
    
    Endpoints:
    - GET    /api/productos/          - Listar productos
    - POST   /api/productos/          - Crear producto
    - GET    /api/productos/{id}/     - Ver detalle
    - PUT    /api/productos/{id}/     - Actualizar completo
    - PATCH  /api/productos/{id}/     - Actualizar parcial
    - DELETE /api/productos/{id}/     - Eliminar (soft delete)
    - POST   /api/productos/{id}/activar/         - Activar
    - POST   /api/productos/{id}/desactivar/      - Desactivar
    - GET    /api/productos/por-empresa/{empresa_id}/  - Por empresa
    - GET    /api/productos/precios-multi-moneda/      - Precios en múltiples monedas
    """
    queryset = Producto.objects.select_related('empresa').all()
    permission_classes = [IsAuthenticated]
    
    # Filtros y búsqueda
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['activo', 'tipo', 'empresa']
    search_fields = ['codigo', 'nombre', 'descripcion', 'empresa__nombre']
    ordering_fields = ['created_at', 'nombre', 'codigo', 'precio_usd']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción
        """
        if self.action == 'list':
            return ProductoListSerializer
        elif self.action == 'retrieve':
            return ProductoDetailSerializer
        elif self.action == 'create':
            return ProductoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductoUpdateSerializer
        elif self.action == 'precios_multi_moneda':
            return ProductoPreciosSerializer
        return ProductoDetailSerializer
    
    def get_queryset(self):
        """
        Personaliza el queryset según parámetros de consulta
        """
        queryset = super().get_queryset()
        
        # Filtrar por estado activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)
        
        # Filtrar por empresa
        empresa_id = self.request.query_params.get('empresa_id', None)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por rango de precio
        precio_min = self.request.query_params.get('precio_min', None)
        precio_max = self.request.query_params.get('precio_max', None)
        
        if precio_min:
            queryset = queryset.filter(precio_usd__gte=Decimal(precio_min))
        if precio_max:
            queryset = queryset.filter(precio_usd__lte=Decimal(precio_max))
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: desactiva el producto en lugar de eliminarlo
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        
        return Response(
            {'message': 'Producto desactivado exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Endpoint personalizado para activar un producto
        POST /api/productos/{id}/activar/
        """
        producto = self.get_object()
        producto.activo = True
        producto.save()
        
        serializer = self.get_serializer(producto)
        return Response(
            {
                'message': 'Producto activado exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Endpoint personalizado para desactivar un producto
        POST /api/productos/{id}/desactivar/
        """
        producto = self.get_object()
        producto.activo = False
        producto.save()
        
        serializer = self.get_serializer(producto)
        return Response(
            {
                'message': 'Producto desactivado exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint para listar solo productos activos
        GET /api/productos/activos/
        """
        activos = self.get_queryset().filter(activo=True)
        page = self.paginate_queryset(activos)
        
        if page is not None:
            serializer = ProductoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductoListSerializer(activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_empresa(self, request):
        """
        Endpoint para listar productos por empresa
        GET /api/productos/por-empresa/?empresa_id=1
        """
        empresa_id = request.query_params.get('empresa_id')
        
        if not empresa_id:
            return Response(
                {'error': 'Se requiere el parámetro empresa_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        productos = self.get_queryset().filter(empresa_id=empresa_id)
        serializer = ProductoListSerializer(productos, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def precios_multi_moneda(self, request):
        """
        Endpoint para obtener precios en múltiples monedas
        GET /api/productos/precios-multi-moneda/?tasa_cop=4000&tasa_eur=0.92
        """
        tasa_cop = request.query_params.get('tasa_cop', '4000')
        tasa_eur = request.query_params.get('tasa_eur', '0.92')
        
        productos = self.get_queryset()
        serializer = ProductoPreciosSerializer(
            productos,
            many=True,
            context={
                'tasa_cop': Decimal(tasa_cop),
                'tasa_eur': Decimal(tasa_eur)
            }
        )
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """
        Endpoint para agrupar productos por tipo
        GET /api/productos/por-tipo/
        """
        tipos = self.get_queryset().values('tipo').distinct()
        resultado = []
        
        for tipo_dict in tipos:
            tipo = tipo_dict['tipo']
            productos = self.get_queryset().filter(tipo=tipo)
            resultado.append({
                'tipo': tipo,
                'tipo_display': dict(Producto.tipo.field.choices).get(tipo),
                'cantidad': productos.count(),
                'productos': ProductoListSerializer(productos, many=True).data
            })
        
        return Response(resultado)
    
    def create(self, request, *args, **kwargs):
        """
        Override create para personalizar la respuesta
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Producto creado exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """
        Override update para personalizar la respuesta
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            {
                'message': 'Producto actualizado exitosamente',
                'data': serializer.data
            }
        )
