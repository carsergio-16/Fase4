"""Clase Reserva: integra cliente, servicio, duración y estado."""

from entidades import Cliente, EntidadBase
from excepciones import (
    OperacionNoPermitidaError,
    ReservaError,
    SoftwareFJError,
)
from registro import log
from servicios import Servicio


# Reserva de un servicio por parte de un cliente.
class Reserva(EntidadBase):

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float) -> None:
        super().__init__(prefijo="RES")
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio válido.")

        servicio.verificar_disponibilidad()
        servicio.validar_parametros(horas)

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = Reserva.PENDIENTE

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    def confirmar(self) -> None:
        # Pasa la reserva de PENDIENTE a CONFIRMADA.
        if self._estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado}."
            )
        self._servicio.verificar_disponibilidad()
        self._estado = Reserva.CONFIRMADA
        log.info("Reserva %s confirmada.", self.id)

    def cancelar(self) -> None:
        # Cancela la reserva si aún no estaba cancelada.
        if self._estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        self._estado = Reserva.CANCELADA
        log.info("Reserva %s cancelada.", self.id)

    def procesar(self, con_iva: bool = True, descuento: float = 0.0) -> float | None:
        # Confirma la reserva, calcula el costo total y usa try/except/else/finally + encadenamiento.
        try:
            self.confirmar()
            total = self._servicio.calcular_costo(
                self._horas, con_iva=con_iva, descuento=descuento
            )
        except SoftwareFJError as error:
            try:
                raise ReservaError(f"No se pudo procesar la reserva {self.id}.") from error
            except ReservaError as envuelto:
                log.error("%s Causa: %s", envuelto, error)
            return None
        else:
            log.info("Reserva %s procesada. Total: $%s", self.id, f"{total:,.2f}")
            return total
        finally:
            log.info("Fin del procesamiento de la reserva %s.", self.id)

    def describir(self) -> str:
        return (
            f"Reserva [{self.id}] | {self._cliente.nombre} | "
            f"{self._servicio.nombre} | {self._horas} h | {self._estado}"
        )
