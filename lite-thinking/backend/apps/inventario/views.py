"""
Views (API endpoints) para Inventario
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Inventario, MovimientoInventario
from .serializers import (
    InventarioListSerializer,
    InventarioDetailSerializer,
    InventarioCreateSerializer,
    InventarioUpdateSerializer,
    MovimientoInventarioSerializer,
    MovimientoInventarioCreateSerializer,
    ReservaInventarioSerializer
)


class InventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Inventarios
    
    Endpoints:
    - GET    /api/inventarios/              - Listar inventarios
    - POST   /api/inventarios/              - Crear inventario
    - GET    /api/inventarios/{id}/         - Ver detalle
    - PUT    /api/inventarios/{id}/         - Actualizar
    - PATCH  /api/inventarios/{id}/         - Actualizar parcial
    - DELETE /api/inventarios/{id}/         - Eliminar
    - POST   /api/inventarios/{id}/entrada/        - Registrar entrada
    - POST   /api/inventarios/{id}/salida/         - Registrar salida
    - POST   /api/inventarios/{id}/ajustar/        - Ajustar inventario
    - POST   /api/inventarios/{id}/reservar/       - Reservar cantidad
    - POST   /api/inventarios/{id}/liberar-reserva/ - Liberar reserva
    - GET    /api/inventarios/bajo-stock/          - Stock bajo
    - GET    /api/inventarios/sin-stock/           - Sin stock
    """
    queryset = Inventario.objects.select_related('producto', 'producto__empresa').all()
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producto', 'producto__empresa']
    search_fields = ['producto__codigo', 'producto__nombre', 'ubicacion']
    ordering_fields = ['cantidad_actual', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado"""
        if self.action == 'list':
            return InventarioListSerializer
        elif self.action == 'retrieve':
            return InventarioDetailSerializer
        elif self.action == 'create':
            return InventarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InventarioUpdateSerializer
        return InventarioDetailSerializer
    
    @action(detail=True, methods=['post'])
    def entrada(self, request, pk=None):
        """
        Registrar entrada de inventario
        POST /api/inventarios/{id}/entrada/
        Body: {"cantidad": 10, "motivo": "Compra"}
        """
        inventario = self.get_object()
        serializer = MovimientoInventarioCreateSerializer(
            data={
                'inventario_id': inventario.id,
                'tipo': 'entrada',
                'cantidad': request.data.get('cantidad'),
                'motivo': request.data.get('motivo', '')
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            movimiento = serializer.save()
            return Response({
                'message': 'Entrada registrada exitosamente',
                'movimiento': MovimientoInventarioSerializer(movimiento).data,
                'inventario': InventarioDetailSerializer(inventario).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def salida(self, request, pk=None):
        """
        Registrar salida de inventario
        POST /api/inventarios/{id}/salida/
        Body: {"cantidad": 5, "motivo": "Venta"}
        """
        inventario = self.get_object()
        serializer = MovimientoInventarioCreateSerializer(
            data={
                'inventario_id': inventario.id,
                'tipo': 'salida',
                'cantidad': request.data.get('cantidad'),
                'motivo': request.data.get('motivo', '')
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                movimiento = serializer.save()
                return Response({
                    'message': 'Salida registrada exitosamente',
                    'movimiento': MovimientoInventarioSerializer(movimiento).data,
                    'inventario': InventarioDetailSerializer(inventario).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def ajustar(self, request, pk=None):
        """
        Ajustar inventario a una cantidad específica
        POST /api/inventarios/{id}/ajustar/
        Body: {"cantidad": 50, "motivo": "Conteo físico"}
        """
        inventario = self.get_object()
        cantidad = request.data.get('cantidad')
        motivo = request.data.get('motivo', '')
        
        if cantidad is None:
            return Response(
                {'error': 'Se requiere el campo cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inventario.ajustar_inventario(
                int(cantidad),
                motivo,
                request.user
            )
            
            return Response({
                'message': 'Inventario ajustado exitosamente',
                'inventario': InventarioDetailSerializer(inventario).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reservar(self, request, pk=None):
        """
        Reservar cantidad de inventario
        POST /api/inventarios/{id}/reservar/
        Body: {"cantidad": 3}
        """
        inventario = self.get_object()
        serializer = ReservaInventarioSerializer(
            data=request.data,
            context={'inventario': inventario}
        )
        
        if serializer.is_valid():
            try:
                inventario.reservar(serializer.validated_data['cantidad'])
                return Response({
                    'message': 'Cantidad reservada exitosamente',
                    'inventario': InventarioDetailSerializer(inventario).data
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def liberar_reserva(self, request, pk=None):
        """
        Liberar reserva de inventario
        POST /api/inventarios/{id}/liberar-reserva/
        Body: {"cantidad": 3}
        """
        inventario = self.get_object()
        cantidad = request.data.get('cantidad')
        
        if not cantidad:
            return Response(
                {'error': 'Se requiere el campo cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inventario.liberar_reserva(int(cantidad))
            return Response({
                'message': 'Reserva liberada exitosamente',
                'inventario': InventarioDetailSerializer(inventario).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """
        Listar inventarios con stock bajo
        GET /api/inventarios/bajo-stock/
        """
        inventarios_bajo = [
            inv for inv in self.get_queryset()
            if inv.cantidad_disponible <= inv.producto.stock_minimo
        ]
        
        serializer = InventarioListSerializer(inventarios_bajo, many=True)
        return Response({
            'count': len(inventarios_bajo),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        """
        Listar inventarios sin stock
        GET /api/inventarios/sin-stock/
        """
        inventarios_sin = [
            inv for inv in self.get_queryset()
            if inv.cantidad_disponible <= 0
        ]
        
        serializer = InventarioListSerializer(inventarios_sin, many=True)
        return Response({
            'count': len(inventarios_sin),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def reporte_stock(self, request):
        """
        Reporte general de stock
        GET /api/inventarios/reporte-stock/
        """
        from django.db.models import Sum
        
        total = self.get_queryset().aggregate(
            total_actual=Sum('cantidad_actual'),
            total_reservado=Sum('cantidad_reservada')
        )
        
        bajo_stock = len([
            inv for inv in self.get_queryset()
            if inv.cantidad_disponible <= inv.producto.stock_minimo
        ])
        
        sin_stock = len([
            inv for inv in self.get_queryset()
            if inv.cantidad_disponible <= 0
        ])
        
        return Response({
            'total_productos': self.get_queryset().count(),
            'total_stock_actual': total['total_actual'] or 0,
            'total_stock_reservado': total['total_reservado'] or 0,
            'productos_bajo_stock': bajo_stock,
            'productos_sin_stock': sin_stock
        })


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar MovimientosInventario (solo lectura)
    
    Endpoints:
    - GET /api/movimientos-inventario/          - Listar movimientos
    - GET /api/movimientos-inventario/{id}/     - Ver detalle
    """
    queryset = MovimientoInventario.objects.select_related(
        'inventario',
        'inventario__producto',
        'usuario'
    ).all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'inventario', 'usuario']
    search_fields = ['inventario__producto__codigo', 'motivo']
    ordering_fields = ['fecha']
    ordering = ['-fecha']
    
    @action(detail=False, methods=['get'])
    def por_producto(self, request):
        """
        Movimientos de un producto específico
        GET /api/movimientos-inventario/por-producto/?producto_id=1
        """
        producto_id = request.query_params.get('producto_id')
        
        if not producto_id:
            return Response(
                {'error': 'Se requiere el parámetro producto_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movimientos = self.get_queryset().filter(
            inventario__producto_id=producto_id
        )
        
        page = self.paginate_queryset(movimientos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(movimientos, many=True)
        return Response(serializer.data)
