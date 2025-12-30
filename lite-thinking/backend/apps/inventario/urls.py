"""
URLs para la app Inventario
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventarioViewSet, MovimientoInventarioViewSet

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'inventarios', InventarioViewSet, basename='inventario')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

# URLs de la app
urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints generados automáticamente:

INVENTARIOS:
------------
Lista y Creación:
- GET    /api/inventario/inventarios/              - Listar inventarios
- POST   /api/inventario/inventarios/              - Crear inventario

Detalle:
- GET    /api/inventario/inventarios/{id}/         - Ver detalle
- PUT    /api/inventario/inventarios/{id}/         - Actualizar
- PATCH  /api/inventario/inventarios/{id}/         - Actualizar parcial
- DELETE /api/inventario/inventarios/{id}/         - Eliminar

Movimientos:
- POST   /api/inventario/inventarios/{id}/entrada/        - Registrar entrada
- POST   /api/inventario/inventarios/{id}/salida/         - Registrar salida
- POST   /api/inventario/inventarios/{id}/ajustar/        - Ajustar inventario

Reservas:
- POST   /api/inventario/inventarios/{id}/reservar/       - Reservar cantidad
- POST   /api/inventario/inventarios/{id}/liberar-reserva/ - Liberar reserva

Reportes:
- GET    /api/inventario/inventarios/bajo-stock/   - Stock bajo
- GET    /api/inventario/inventarios/sin-stock/    - Sin stock
- GET    /api/inventario/inventarios/reporte-stock/ - Reporte general

MOVIMIENTOS (Solo lectura):
---------------------------
- GET    /api/inventario/movimientos/              - Listar movimientos
- GET    /api/inventario/movimientos/{id}/         - Ver detalle
- GET    /api/inventario/movimientos/por-producto/?producto_id=1 - Por producto

Filtros:
- GET /api/inventario/inventarios/?producto=1
- GET /api/inventario/inventarios/?search=laptop
- GET /api/inventario/movimientos/?tipo=entrada
- GET /api/inventario/movimientos/?fecha=2024-12-29
"""
