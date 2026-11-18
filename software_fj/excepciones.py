"""Excepciones personalizadas del sistema Software FJ.

Todas heredan de ErrorSoftwareFJ, de modo que el programa pueda capturar
cualquier error propio del dominio con un solo ``except ErrorSoftwareFJ``.
Los demás integrantes del grupo pueden añadir aquí sus propias excepciones
(por ejemplo ClienteInvalidoError o ReservaInvalidaError).
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de todo el sistema."""

    def __init__(self, mensaje: str, codigo: str = "SFJ-000"):
        super().__init__(mensaje)  # Guarda el mensaje en la excepción estándar
        self.mensaje = mensaje     # Mensaje legible para el usuario/log
        self.codigo = codigo       # Código corto para identificar el tipo de error

    def __str__(self) -> str:
        # Formato uniforme: [CODIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ParametroInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato es inválido, falta o tiene un tipo incorrecto."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-001")


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta usar un servicio que no está disponible."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-002")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce un resultado inválido."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-003")


class ClienteInvalidoError(ErrorSoftwareFJ, ValueError):
    """Datos de cliente inválidos (nombre vacío, correo mal formado, etc.).

    Hereda también de ValueError para que el código que ya capturaba
    ValueError siga funcionando sin cambios.
    """

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-004")


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva no puede crearse o procesarse correctamente."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-005")


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando el estado actual de la reserva no permite la operación."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-006")
