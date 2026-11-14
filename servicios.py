from abc import abstractmethod
from entidades import Entidad
from excepciones_y_logs import DatoInvalidoError, ServicioNoDisponibleError, CalculoInconsistenteError

class Servicio(Entidad):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base debe ser mayor a cero.")
        
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion: int, **kwargs):
        """Valida las reglas específicas de cada tipo de servicio."""
        if not self._disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._nombre}' no está disponible actualmente.")
        if not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError("La duración debe ser un número entero mayor a 0.")

    @abstractmethod
    def calcular_costo_base(self, duracion: int) -> float:
        """Calcula el costo sin impuestos ni descuentos."""
        pass

    # Simulación de sobrecarga de métodos mediante argumentos opcionales
    def calcular_costo(self, duracion: int, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """
        Calcula el costo total permitiendo múltiples combinaciones:
        - Solo duración: calcular_costo(2)
        - Con impuestos: calcular_costo(2, impuesto=0.19)
        - Con impuestos y descuento: calcular_costo(2, impuesto=0.19, descuento=0.10)
        """
        if impuesto < 0 or descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError("Porcentajes de impuesto o descuento fuera de rango lógico.")

        subtotal = self.calcular_costo_base(duracion)
        monto_descuento = subtotal * descuento
        base_gravable = subtotal - monto_descuento
        total = base_gravable * (1 + impuesto)

        if total <= 0:
            raise CalculoInconsistenteError("El cálculo final del servicio arrojó un valor menor o igual a cero.")
        
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio especializado para alquiler de salas de reuniones o capacitación."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, capacidad_max: int):
        super().__init__(id_servicio, nombre, tarifa_hora)
        if capacidad_max <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser mayor a 0.")
        self.capacidad_max = capacidad_max

    def validar_parametros(self, duracion: int, **kwargs):
        super().validar_parametros(duracion, **kwargs)
        asistentes = kwargs.get("asistentes", 1)
        if asistentes <= 0 or asistentes > self.capacidad_max:
            raise DatoInvalidoError(
                f"Cantidad de asistentes ({asistentes}) inválida. Máximo permitido: {self.capacidad_max}."
            )

    def calcular_costo_base(self, duracion: int) -> float:
        return self._tarifa_base * duracion

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self.disponible else "Ocupada"
        return f"Sala [{self.id}]: {self.nombre} | Capacidad: {self.capacidad_max} pers. | ${self._tarifa_base}/h | {estado}"


class AlquilerEquipo(Servicio):
    """Servicio especializado para préstamo de hardware y equipos."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_dia: float, stock: int):
        super().__init__(id_servicio, nombre, tarifa_dia, disponible=(stock > 0))
        if stock < 0:
            raise DatoInvalidoError("El stock inicial no puede ser negativo.")
        self.stock = stock

    def validar_parametros(self, duracion: int, **kwargs):
        super().validar_parametros(duracion, **kwargs)
        cantidad = kwargs.get("cantidad", 1)
        if cantidad <= 0 or cantidad > self.stock:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente para '{self.nombre}'. Solicitado: {cantidad}, Disponible: {self.stock}."
            )

    def reducir_stock(self, cantidad: int):
        self.stock -= cantidad
        if self.stock == 0:
            self.disponible = False

    def calcular_costo_base(self, duracion: int) -> float:
        # Incluye un cargo fijo de seguro del 5% sobre la tarifa base
        return (self._tarifa_base * duracion) * 1.05

    def obtener_resumen(self) -> str:
        return f"Equipo [{self.id}]: {self.nombre} | Stock: {self.stock} unid. | ${self._tarifa_base}/día"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de consultoría técnica o arquitectura de software."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, especialidad: str):
        super().__init__(id_servicio, nombre, tarifa_hora)
        if not especialidad or not especialidad.strip():
            raise DatoInvalidoError("Debe especificar el área de especialidad de la asesoría.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: int, **kwargs):
        super().validar_parametros(duracion, **kwargs)
        if duracion < 2:
            raise DatoInvalidoError("Las asesorías especializadas requieren un mínimo de 2 horas.")

    def calcular_costo_base(self, duracion: int) -> float:
        return self._tarifa_base * duracion

    def obtener_resumen(self) -> str:
        return f"Asesoría [{self.id}]: {self.nombre} ({self.especialidad}) | ${self._tarifa_base}/h"
