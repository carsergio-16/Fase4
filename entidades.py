"""Módulo de Entidades del Sistema Software FJ.
Contiene la clase abstracta EntidadBase y la clase Cliente con validaciones
robustas, encapsulación y registro en el sistema de logs.
"""

from abc import ABC, abstractmethod
from excepciones import ClienteInvalidoError, ParametroFaltanteError
from registro import log


# Clase abstracta que representa entidades generales del sistema Software FJ.
class EntidadBase(ABC):

    def __init__(self, identificador: str):
        if not identificador or not isinstance(identificador, str) or not identificador.strip():
            log.error("Intento de instanciar EntidadBase con identificador vacío o inválido.")
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio y no puede estar vacío.")
        self._identificador = identificador.strip()

    @property
    def identificador(self) -> str:
        # Devuelve el identificador único de la entidad.
        return self._identificador

    @abstractmethod
    def obtener_detalles(self) -> str:
        # Método abstracto para retornar los detalles específicos de la entidad.
        pass


# Clase Cliente que hereda de EntidadBase, aplicando encapsulación y validaciones estrictas.
class Cliente(EntidadBase):

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        log.info(f"Cliente registrado exitosamente: ID={self._identificador}, Nombre={self._nombre}")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            log.warning(f"Validación fallida de nombre de cliente: '{valor}'")
            raise ClienteInvalidoError(
                f"Nombre de cliente inválido: '{valor}'. Debe ser un texto de al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not isinstance(valor, str) or "@" not in valor or "." not in valor:
            log.warning(f"Validación fallida de correo de cliente: '{valor}'")
            raise ClienteInvalidoError(
                f"Correo electrónico inválido: '{valor}'. Debe contener '@' y un dominio válido."
            )
        self._correo = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.isdigit() or len(valor) < 7:
            log.warning(f"Validación fallida de teléfono de cliente: '{valor}'")
            raise ClienteInvalidoError(
                f"Teléfono inválido: '{valor}'. Debe contener únicamente dígitos y al menos 7 caracteres."
            )
        self._telefono = valor.strip()

    def obtener_detalles(self) -> str:
        # Retorna una representación detallada del cliente.
        return (
            f"Cliente [ID: {self.identificador}] - "
            f"Nombre: {self.nombre} | "
            f"Correo: {self.correo} | "
            f"Teléfono: {self.telefono}"
        )
