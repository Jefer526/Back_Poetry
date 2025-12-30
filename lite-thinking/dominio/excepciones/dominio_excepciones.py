"""
Excepciones de Dominio - Lite Thinking
Excepciones específicas del negocio sin dependencias de frameworks
"""


class DominioExcepcion(Exception):
    """Excepción base para todas las excepciones de dominio"""
    def __init__(self, mensaje: str, codigo: str = "ERROR_DOMINIO"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)


class EntidadNoEncontrada(DominioExcepcion):
    """Se lanza cuando no se encuentra una entidad solicitada"""
    def __init__(self, entidad: str, identificador: any):
        mensaje = f"{entidad} con identificador '{identificador}' no encontrada"
        super().__init__(mensaje, "ENTIDAD_NO_ENCONTRADA")
        self.entidad = entidad
        self.identificador = identificador


class EntidadYaExiste(DominioExcepcion):
    """Se lanza cuando se intenta crear una entidad que ya existe"""
    def __init__(self, entidad: str, campo: str, valor: any):
        mensaje = f"{entidad} con {campo} '{valor}' ya existe"
        super().__init__(mensaje, "ENTIDAD_YA_EXISTE")
        self.entidad = entidad
        self.campo = campo
        self.valor = valor


class ValidacionDominioError(DominioExcepcion):
    """Se lanza cuando falla una validación de reglas de negocio"""
    def __init__(self, mensaje: str, campo: str = None):
        super().__init__(mensaje, "VALIDACION_DOMINIO_ERROR")
        self.campo = campo


class InventarioInsuficiente(DominioExcepcion):
    """Se lanza cuando no hay suficiente inventario para una operación"""
    def __init__(self, producto_id: int, disponible: int, solicitado: int):
        mensaje = (
            f"Inventario insuficiente para producto ID {producto_id}. "
            f"Disponible: {disponible}, Solicitado: {solicitado}"
        )
        super().__init__(mensaje, "INVENTARIO_INSUFICIENTE")
        self.producto_id = producto_id
        self.disponible = disponible
        self.solicitado = solicitado


class OperacionNoPermitida(DominioExcepcion):
    """Se lanza cuando se intenta realizar una operación no permitida"""
    def __init__(self, mensaje: str, razon: str = None):
        super().__init__(mensaje, "OPERACION_NO_PERMITIDA")
        self.razon = razon


class PermisosDenegados(DominioExcepcion):
    """Se lanza cuando un usuario no tiene permisos para una operación"""
    def __init__(self, usuario_id: int, operacion: str):
        mensaje = f"Usuario ID {usuario_id} no tiene permisos para: {operacion}"
        super().__init__(mensaje, "PERMISOS_DENEGADOS")
        self.usuario_id = usuario_id
        self.operacion = operacion


class EstadoInvalido(DominioExcepcion):
    """Se lanza cuando una entidad está en un estado inválido para una operación"""
    def __init__(self, entidad: str, estado_actual: str, operacion: str):
        mensaje = (
            f"No se puede realizar '{operacion}' en {entidad} "
            f"con estado '{estado_actual}'"
        )
        super().__init__(mensaje, "ESTADO_INVALIDO")
        self.entidad = entidad
        self.estado_actual = estado_actual
        self.operacion = operacion


class DatosInconsistentes(DominioExcepcion):
    """Se lanza cuando hay inconsistencia en los datos"""
    def __init__(self, mensaje: str, detalles: dict = None):
        super().__init__(mensaje, "DATOS_INCONSISTENTES")
        self.detalles = detalles or {}


class ReglaNegocioViolada(DominioExcepcion):
    """Se lanza cuando se viola una regla de negocio"""
    def __init__(self, regla: str, mensaje: str = None):
        mensaje_final = mensaje or f"Regla de negocio violada: {regla}"
        super().__init__(mensaje_final, "REGLA_NEGOCIO_VIOLADA")
        self.regla = regla
