"""
URLs para la app Empresas
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpresaViewSet

# Crear router para el ViewSet
router = DefaultRouter()
router.register(r'', EmpresaViewSet, basename='empresa')

# URLs de la app
urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints generados automáticamente:

Lista y Creación:
- GET    /api/empresas/              - Listar empresas
- POST   /api/empresas/              - Crear empresa

Detalle:
- GET    /api/empresas/{id}/         - Ver detalle
- PUT    /api/empresas/{id}/         - Actualizar completo
- PATCH  /api/empresas/{id}/         - Actualizar parcial
- DELETE /api/empresas/{id}/         - Eliminar (soft delete)

Acciones personalizadas:
- POST   /api/empresas/{id}/activar/    - Activar empresa
- POST   /api/empresas/{id}/desactivar/ - Desactivar empresa
- GET    /api/empresas/activas/         - Solo activas
- GET    /api/empresas/inactivas/       - Solo inactivas

Filtros y búsqueda:
- GET /api/empresas/?activa=true     - Filtrar por estado
- GET /api/empresas/?search=term     - Buscar por NIT, nombre o email
- GET /api/empresas/?ordering=-created_at - Ordenar por fecha
"""
