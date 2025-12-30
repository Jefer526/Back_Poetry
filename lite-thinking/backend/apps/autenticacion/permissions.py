"""
Permisos personalizados para control de acceso - SIN EMPRESA
"""
from rest_framework import permissions


class EsAdministrador(permissions.BasePermission):
    """
    Permiso: Solo usuarios administradores
    """
    message = "Solo los administradores tienen acceso a esta función"
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.es_administrador
        )


class EsAdministradorOSoloLectura(permissions.BasePermission):
    """
    Permiso: Administrador puede todo, Externo solo lectura (GET)
    """
    
    def has_permission(self, request, view):
        # Permitir lectura a todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Escritura solo para administradores
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.es_administrador
        )