"""
Configuración de la app IA
"""
from django.apps import AppConfig


class IAConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.ia'
    verbose_name = 'Inteligencia Artificial'
