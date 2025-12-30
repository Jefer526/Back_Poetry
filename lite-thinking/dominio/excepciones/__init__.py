"""
Excepciones de Dominio - Lite Thinking
"""

from .dominio_excepciones import (
    DominioExcepcion,
    EntidadNoEncontrada,
    EntidadYaExiste,
    ValidacionDominioError,
    InventarioInsuficiente,
    OperacionNoPermitida,
    PermisosDenegados,
    EstadoInvalido,
    DatosInconsistentes,
    ReglaNegocioViolada
)

__all__ = [
    'DominioExcepcion',
    'EntidadNoEncontrada',
    'EntidadYaExiste',
    'ValidacionDominioError',
    'InventarioInsuficiente',
    'OperacionNoPermitida',
    'PermisosDenegados',
    'EstadoInvalido',
    'DatosInconsistentes',
    'ReglaNegocioViolada'
]
