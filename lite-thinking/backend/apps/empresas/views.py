"""
Views (API endpoints) para Empresas
Usando ViewSets de Django REST Framework
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Empresa
from .serializers import (
    EmpresaListSerializer,
    EmpresaDetailSerializer,
    EmpresaCreateSerializer,
    EmpresaUpdateSerializer
)


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Empresas
    Proporciona operaciones CRUD completas
    
    Endpoints:
    - GET    /api/empresas/          - Listar empresas
    - POST   /api/empresas/          - Crear empresa
    - GET    /api/empresas/{id}/     - Ver detalle
    - PUT    /api/empresas/{id}/     - Actualizar completo
    - PATCH  /api/empresas/{id}/     - Actualizar parcial
    - DELETE /api/empresas/{id}/     - Eliminar
    - POST   /api/empresas/{id}/activar/    - Activar empresa
    - POST   /api/empresas/{id}/desactivar/ - Desactivar empresa
    """
    queryset = Empresa.objects.all()
    permission_classes = [IsAuthenticated]
    
    # Filtros y búsqueda
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['activa', 'nit']
    search_fields = ['nit', 'nombre', 'email']
    ordering_fields = ['created_at', 'nombre', 'nit']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción
        Implementa el patrón de especialización de serializers
        """
        if self.action == 'list':
            return EmpresaListSerializer
        elif self.action == 'retrieve':
            return EmpresaDetailSerializer
        elif self.action == 'create':
            return EmpresaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmpresaUpdateSerializer
        return EmpresaDetailSerializer
    
    def get_queryset(self):
        """
        Personaliza el queryset según parámetros de consulta
        """
        queryset = super().get_queryset()
        
        # Filtrar por estado activo (opcional)
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            activa_bool = activa.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activa=activa_bool)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: en lugar de eliminar, desactiva la empresa
        """
        instance = self.get_object()
        instance.activa = False
        instance.save()
        
        return Response(
            {'message': 'Empresa desactivada exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Endpoint personalizado para activar una empresa
        POST /api/empresas/{id}/activar/
        """
        empresa = self.get_object()
        empresa.activa = True
        empresa.save()
        
        serializer = self.get_serializer(empresa)
        return Response(
            {
                'message': 'Empresa activada exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Endpoint personalizado para desactivar una empresa
        POST /api/empresas/{id}/desactivar/
        """
        empresa = self.get_object()
        empresa.activa = False
        empresa.save()
        
        serializer = self.get_serializer(empresa)
        return Response(
            {
                'message': 'Empresa desactivada exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Endpoint para listar solo empresas activas
        GET /api/empresas/activas/
        """
        activas = self.queryset.filter(activa=True)
        serializer = EmpresaListSerializer(activas, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivas(self, request):
        """
        Endpoint para listar solo empresas inactivas
        GET /api/empresas/inactivas/
        """
        inactivas = self.queryset.filter(activa=False)
        serializer = EmpresaListSerializer(inactivas, many=True)
        
        return Response(serializer.data)
    
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
                'message': 'Empresa creada exitosamente',
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
                'message': 'Empresa actualizada exitosamente',
                'data': serializer.data
            }
        )
