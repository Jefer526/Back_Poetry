"""
URLs para la app Productos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

# Crear router para el ViewSet
router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

# URLs de la app
urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints generados automáticamente:

Lista y Creación:
- GET    /api/productos/              - Listar productos
- POST   /api/productos/              - Crear producto

Detalle:
- GET    /api/productos/{id}/         - Ver detalle
- PUT    /api/productos/{id}/         - Actualizar completo
- PATCH  /api/productos/{id}/         - Actualizar parcial
- DELETE /api/productos/{id}/         - Eliminar (soft delete)

Acciones personalizadas:
- POST   /api/productos/{id}/activar/            - Activar producto
- POST   /api/productos/{id}/desactivar/         - Desactivar producto
- GET    /api/productos/activos/                 - Solo activos
- GET    /api/productos/por-empresa/?empresa_id=1 - Por empresa
- GET    /api/productos/precios-multi-moneda/    - Precios en varias monedas
- GET    /api/productos/por-tipo/                - Agrupados por tipo

Filtros y búsqueda:
- GET /api/productos/?activo=true              - Filtrar por estado
- GET /api/productos/?tipo=fisico              - Filtrar por tipo
- GET /api/productos/?empresa=1                - Filtrar por empresa
- GET /api/productos/?search=laptop            - Buscar por código, nombre
- GET /api/productos/?precio_min=100&precio_max=500  - Rango de precio
- GET /api/productos/?ordering=-precio_usd     - Ordenar por precio
"""
