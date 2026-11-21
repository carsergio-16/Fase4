"""Módulo de Entidades del Sistema Software FJ."""

from abc import ABC, abstractmethod
from excepciones import ClienteInvalidoError, ParametroFaltanteError
from registro import log


# Clase abstracta base para entidades del dominio con ID autogenerado.
class EntidadBase(ABC):
    _secuencia: int = 0

    def __init__(self, prefijo: str = "ENT") -> None:
        EntidadBase._secuencia += 1
        self._id: str = f"{prefijo}-{EntidadBase._secuencia:04d}"

    @property
    def id(self) -> str:
        # Identificador único de la entidad.
        return self._id

    @abstractmethod
    def describir(self) -> str:
        # Representación legible de la entidad.
        pass

    def __str__(self) -> str:
        return self.describir()


# Clase Cliente con encapsulación y validaciones estrictas.
class Cliente(EntidadBase):

    def __init__(
        self,
        nombre: str,
        documento: str = "",
        correo: str = "",
        telefono: str = "",
    ) -> None:
        super().__init__(prefijo="CLI")
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        log.info("Cliente registrado: %s (%s)", self._nombre, self._id)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            log.warning("Nombre de cliente inválido: %r", valor)
            raise ClienteInvalidoError(
                "El nombre del cliente debe tener al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 6:
            log.warning("Documento de cliente inválido: %r", valor)
            raise ClienteInvalidoError(
                "El documento debe contener al menos 6 dígitos numéricos."
            )
        self._documento = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            log.warning("Correo de cliente inválido: %r", valor)
            raise ClienteInvalidoError(
                "El correo electrónico no tiene un formato válido."
            )
        self._correo = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 7:
            log.warning("Teléfono de cliente inválido: %r", valor)
            raise ClienteInvalidoError(
                "El teléfono debe contener al menos 7 dígitos numéricos."
            )
        self._telefono = valor.strip()

    @classmethod
    def crear_seguro(cls, *datos) -> "Cliente | None":
        # Valida parámetros mínimos y crea el cliente registrando errores sin caer.
        if len(datos) < 4:
            log.error("Faltan parámetros para crear cliente. Recibidos: %s", len(datos))
            raise ParametroFaltanteError(
                "Se requieren nombre, documento, correo y teléfono para registrar un cliente."
            )
        try:
            nombre, documento, correo, telefono = datos[:4]
            return cls(nombre=nombre, documento=documento, correo=correo, telefono=telefono)
        except ClienteInvalidoError as error:
            log.error("Error al crear cliente de forma segura: %s", error)
            return None

    def describir(self) -> str:
        return (
            f"Cliente [{self.id}] {self._nombre} | Doc: {self._documento} | "
            f"Correo: {self._correo} | Tel: {self._telefono}"
        )
