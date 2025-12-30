"""
URL configuration for Lite Thinking project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('api/empresas/', include('backend.apps.empresas.urls')),
    path('api/productos/', include('backend.apps.productos.urls')),
    path('api/inventario/', include('backend.apps.inventario.urls')),
    # path('api/auth/', include('backend.apps.autenticacion.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar el admin
admin.site.site_header = "Lite Thinking - Administración"
admin.site.site_title = "Lite Thinking Admin"
admin.site.index_title = "Panel de Administración"