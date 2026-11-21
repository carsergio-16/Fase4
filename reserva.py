"""Clase Reserva: integra cliente, servicio, duración y estado."""

from entidades import Cliente, EntidadBase
from excepciones import (OperacionNoPermitidaError, ReservaError, SoftwareFJError)
from registro import log
from servicios import Servicio


# Clase Reserva que hereda de EntidadBase para obtener un ID único y representar una reserva.
class Reserva(EntidadBase):

    # Estados válidos del ciclo de vida de una reserva.
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float) -> None:
        # Genera el identificador con prefijo "RES" desde la clase abstracta EntidadBase.
        super().__init__(prefijo="RES")
        # Verifica que cliente y servicio sean instancias válidas de sus clases correspondientes.
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio válido.")

        # Valida disponibilidad del servicio y reglas de duración antes de crear la reserva.
        servicio.verificar_disponibilidad()
        servicio.validar_parametros(horas)

        # Almacena los datos encapsulados y deja la reserva en estado inicial PENDIENTE.
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = Reserva.PENDIENTE

    @property
    def estado(self) -> str:
        # Expone el estado actual de la reserva de forma controlada.
        return self._estado

    @property
    def cliente(self) -> Cliente:
        # Expone el cliente asociado a la reserva.
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        # Expone el servicio reservado.
        return self._servicio

    def confirmar(self) -> None:
        # Solo permite confirmar si la reserva sigue en estado PENDIENTE.
        if self._estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado {self._estado}.")
        # Revisa que el servicio siga disponible justo antes de confirmar.
        self._servicio.verificar_disponibilidad()
        self._estado = Reserva.CONFIRMADA
        log.info("Reserva %s confirmada.", self.id)

    def cancelar(self) -> None:
        # Evita cancelar dos veces una reserva que ya está CANCELADA.
        if self._estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        self._estado = Reserva.CANCELADA
        log.info("Reserva %s cancelada.", self.id)

    def procesar(self, con_iva: bool = True, descuento: float = 0.0) -> float | None:
        # Intenta confirmar la reserva y calcular el costo total con IVA y descuento opcionales.
        try:
            self.confirmar()
            total = self._servicio.calcular_costo(self._horas, con_iva=con_iva, descuento=descuento)
        except SoftwareFJError as error:
            # Encadena la excepción original dentro de ReservaError y registra el fallo en el log.
            try:
                raise ReservaError(f"No se pudo procesar la reserva {self.id}.") from error
            except ReservaError as envuelto:
                log.error("%s Causa: %s", envuelto, error)
            return None
        else:
            # Se ejecuta solo si no hubo errores: registra el éxito y retorna el valor total.
            log.info("Reserva %s procesada. Total: $%s", self.id, f"{total:,.2f}")
            return total
        finally:
            # Se ejecuta siempre al finalizar el bloque para dejar trazabilidad del cierre.
            log.info("Fin del procesamiento de la reserva %s.", self.id)

    def describir(self) -> str:
        # Implementa el método abstracto de EntidadBase con un resumen legible de la reserva.
        return (f"Reserva [{self.id}] | {self._cliente.nombre} | "f"{self._servicio.nombre} | {self._horas} h | {self._estado}")
