"""
Configuración de la app Productos
"""
from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.productos'
    verbose_name = 'Productos'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import backend.apps.productos.signals