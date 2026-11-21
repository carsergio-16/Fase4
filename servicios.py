"""Módulo de Servicios del Sistema Software FJ."""

from abc import abstractmethod
from entidades import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from registro import log

IVA_POR_DEFECTO: float = 0.19


# Clase abstracta base para todos los servicios de Software FJ.
class Servicio(EntidadBase):

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        super().__init__(prefijo="SRV")
        self.nombre = nombre
        self.costo_base = tarifa_base
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ServicioInvalidoError("El nombre del servicio es obligatorio.")
        self._nombre = valor.strip()

    @property
    def costo_base(self) -> float:
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor <= 0:
            raise ServicioInvalidoError("La tarifa o costo base debe ser mayor a cero.")
        self._costo_base = float(valor)

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    def marcar_no_disponible(self) -> None:
        self._disponible = False
        log.info("Servicio marcado como no disponible: %s (%s)", self._nombre, self.id)

    def marcar_disponible(self) -> None:
        self._disponible = True
        log.info("Servicio marcado como disponible: %s (%s)", self._nombre, self.id)

    def verificar_disponibilidad(self) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' ({self.id}) no está disponible."
            )

    @abstractmethod
    def validar_parametros(self, horas: float, **kwargs) -> None:
        # Valida duración y parámetros específicos de cada servicio.
        pass

    def _validar_horas_positivas(self, horas: float) -> None:
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or horas <= 0:
            raise ServicioInvalidoError("La duración en horas debe ser mayor que cero.")

    @abstractmethod
    def _subtotal_por_horas(self, horas: float) -> float:
        # Calcula el subtotal antes de descuentos e impuestos.
        pass

    # Sobrecarga simulada mediante argumentos posicionales y opcionales.
    def calcular_costo(
        self,
        horas: float,
        con_iva: bool = False,
        descuento: float = 0.0,
        iva: float = IVA_POR_DEFECTO,
    ) -> float:
        self._validar_horas_positivas(horas)
        if not isinstance(descuento, (int, float)) or isinstance(descuento, bool):
            raise CalculoInconsistenteError("El descuento debe ser un valor numérico.")
        if descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError(
                f"Descuento fuera de rango ({descuento}): debe estar entre 0 y < 1."
            )
        if not isinstance(iva, (int, float)) or isinstance(iva, bool) or iva < 0:
            raise CalculoInconsistenteError("El porcentaje de IVA no puede ser negativo.")

        subtotal = self._subtotal_por_horas(horas)
        if subtotal <= 0:
            raise CalculoInconsistenteError("El subtotal calculado es inválido.")

        con_descuento = subtotal * (1.0 - float(descuento))
        total = con_descuento * (1.0 + float(iva)) if con_iva else con_descuento

        if total <= 0:
            raise CalculoInconsistenteError("El costo total calculado es inconsistente.")

        return round(float(total), 2)

    @abstractmethod
    def describir(self) -> str:
        pass


# Servicio 1: Reserva de salas.
class ReservaSala(Servicio):

    def __init__(self, nombre: str, tarifa_hora: float, capacidad: int) -> None:
        super().__init__(nombre=nombre, tarifa_base=tarifa_hora, disponible=True)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero mayor a 0.")
        self.capacidad = capacidad

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas_positivas(horas)
        if horas > 24:
            raise ServicioInvalidoError("Una reserva de sala no puede superar las 24 horas seguidas.")
        asistentes = kwargs.get("asistentes")
        if asistentes is not None and (asistentes <= 0 or asistentes > self.capacidad):
            raise ServicioInvalidoError(
                f"Asistentes ({asistentes}) fuera de capacidad ({self.capacidad})."
            )

    def _subtotal_por_horas(self, horas: float) -> float:
        return self._costo_base * float(horas)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Sala [{self.id}] {self._nombre} | Cap: {self.capacidad} | "
            f"Tarifa: ${self._costo_base:,.2f}/h | {estado}"
        )


# Servicio 2: Alquiler de equipos.
class AlquilerEquipo(Servicio):
    MAX_HORAS: float = 72.0

    def __init__(self, nombre: str, tarifa_hora: float, categoria_o_stock: str | int) -> None:
        if isinstance(categoria_o_stock, int) and not isinstance(categoria_o_stock, bool):
            disponible = categoria_o_stock > 0
            self.categoria = "Equipo"
            self.stock = categoria_o_stock
        else:
            if not isinstance(categoria_o_stock, str) or not categoria_o_stock.strip():
                raise ServicioInvalidoError("Debe indicar el tipo o categoría del equipo.")
            disponible = True
            self.categoria = categoria_o_stock.strip()
            self.stock = 1

        super().__init__(nombre=nombre, tarifa_base=tarifa_hora, disponible=disponible)

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas_positivas(horas)
        if horas > self.MAX_HORAS:
            raise ServicioInvalidoError(
                f"El alquiler de '{self._nombre}' permite máximo {self.MAX_HORAS:.0f} horas (solicitadas: {horas})."
            )

    def _subtotal_por_horas(self, horas: float) -> float:
        return self._costo_base * float(horas)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Equipo [{self.id}] {self._nombre} ({self.categoria}) | "
            f"Tarifa: ${self._costo_base:,.2f}/h | {estado}"
        )


# Servicio 3: Asesorías especializadas.
class Asesoria(Servicio):

    def __init__(self, nombre: str, tarifa_hora: float, nivel: str = "estándar") -> None:
        super().__init__(nombre=nombre, tarifa_base=tarifa_hora, disponible=True)
        if not isinstance(nivel, str) or not nivel.strip():
            raise ServicioInvalidoError("El nivel o área de la asesoría es obligatorio.")
        self.nivel = nivel.strip()

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas_positivas(horas)
        if horas > 40:
            raise ServicioInvalidoError("Una asesoría no puede programarse por más de 40 horas seguidas.")

    def _subtotal_por_horas(self, horas: float) -> float:
        factor = 1.2 if self.nivel.lower() == "senior" else 1.0
        return self._costo_base * float(horas) * factor

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Asesoría [{self.id}] {self._nombre} ({self.nivel}) | "
            f"Tarifa: ${self._costo_base:,.2f}/h | {estado}"
        )


# Alias por compatibilidad si algún módulo importa AsesoriaEspecializada.
AsesoriaEspecializada = Asesoria
