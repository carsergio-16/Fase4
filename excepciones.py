"""Excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, de modo que el programa principal pueda
capturar cualquier error propio del dominio con un solo `except`.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""


class ValidacionError(SoftwareFJError):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación."""


class ClienteInvalidoError(ValidacionError):
    """Se lanza cuando los datos de un cliente son inválidos."""


class ParametroFaltanteError(ValidacionError):
    """Se lanza cuando falta un parámetro obligatorio."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta usar un servicio que no está disponible."""


class ServicioInvalidoError(ValidacionError):
    """Se lanza cuando los parámetros de un servicio son inválidos."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación que el estado actual no permite."""


class ReservaError(SoftwareFJError):
    """Se lanza cuando una reserva no puede crearse o procesarse."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado inválido."""
