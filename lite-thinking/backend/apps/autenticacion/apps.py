"""
Configuración de la app Autenticación
"""
from django.apps import AppConfig


class AutenticacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.autenticacion'
    verbose_name = 'Autenticación y Usuarios'
