"""Programa principal de Software FJ.

Simula 12 operaciones completas (válidas e inválidas) sin base de datos:
toda la información vive en listas en memoria y solo se escribe el log.
El programa nunca se detiene ante un error: cada operación se aísla.
"""

from entidades import Cliente
from excepciones import SoftwareFJError
from registro import RUTA_LOG, log
from reserva import Reserva
from servicios import AlquilerEquipo, Asesoria, ReservaSala


class SistemaFJ:
    """Fachada que administra las listas internas de clientes, servicios y reservas."""

    def __init__(self) -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, *datos) -> Cliente | None:
        cliente = Cliente.crear_seguro(*datos)
        if cliente:
            self.clientes.append(cliente)
        return cliente

    def crear_servicio(self, clase, *args):
        """Crea un servicio; si los parámetros son inválidos registra el error."""
        try:
            servicio = clase(*args)
        except (SoftwareFJError, TypeError) as error:
            log.error("Creación de servicio fallida (%s): %s", clase.__name__, error)
            return None
        self.servicios.append(servicio)
        log.info("Servicio creado: %s", servicio.describir())
        return servicio

    def reservar(self, cliente, servicio, horas):
        """Crea una reserva y la procesa; devuelve (reserva, total) o (None, None)."""
        try:
            reserva = Reserva(cliente, servicio, horas)
        except SoftwareFJError as error:
            log.error("Reserva fallida: %s", error)
            return None, None
        self.reservas.append(reserva)
        return reserva, reserva.procesar()


def mostrar(numero: int, titulo: str, resultado) -> None:
    """Imprime el resultado de cada operación de forma uniforme."""
    estado = "OK " if resultado else "ERR"
    print(f"{numero:>2}. [{estado}] {titulo}")


def main() -> None:
    sistema = SistemaFJ()
    log.info("=== Inicio de la simulación ===")

    # 1-3: registros de clientes (válido, inválido, inválido)
    ana = sistema.registrar_cliente("Ana Gómez", "1012345678", "ana@correo.com", "3001234567")
    mostrar(1, "Registro válido: Ana Gómez", ana)
    mostrar(2, "Registro inválido: correo sin formato",
            sistema.registrar_cliente("Luis Pérez", "9876543", "luis-correo", "3109876543"))
    mostrar(3, "Registro inválido: nombre vacío",
            sistema.registrar_cliente("", "1234567", "x@correo.com", "3001112233"))
    carlos = sistema.registrar_cliente("Carlos Ruiz", "79456123", "carlos@correo.com", "3205556677")
    mostrar(4, "Registro válido: Carlos Ruiz", carlos)

    # 5-7: creación de servicios (válido, válido, inválido)
    sala = sistema.crear_servicio(ReservaSala, "Sala Innovación", 50000, 10)
    mostrar(5, "Servicio válido: Sala Innovación", sala)
    equipo = sistema.crear_servicio(AlquilerEquipo, "Portátil Gamer", 8000, "Computador")
    mostrar(6, "Servicio válido: Portátil Gamer", equipo)
    mostrar(7, "Servicio inválido: tarifa negativa",
            sistema.crear_servicio(Asesoria, "Asesoría Cloud", -100, "senior"))
    asesoria = sistema.crear_servicio(Asesoria, "Asesoría Cloud", 90000, "senior")
    mostrar(8, "Servicio válido: Asesoría Cloud", asesoria)

    # 9: reserva exitosa con IVA
    reserva, total = sistema.reservar(ana, sala, 3)
    mostrar(9, f"Reserva exitosa (sala 3 h, con IVA): ${total:,.2f}" if total else "Reserva sala", total)

    # 10: reserva fallida por duración fuera de rango
    _, total = sistema.reservar(carlos, equipo, 100)
    mostrar(10, "Reserva fallida: equipo por 100 h (máx. 72)", total)

    # 11: reserva fallida por servicio no disponible
    asesoria.marcar_no_disponible()
    _, total = sistema.reservar(ana, asesoria, 2)
    mostrar(11, "Reserva fallida: servicio no disponible", total)

    # 12: cancelar y volver a confirmar (operación no permitida)
    try:
        reserva.cancelar()
        reserva.confirmar()  # una reserva cancelada no puede confirmarse
        mostrar(12, "Confirmar reserva cancelada", True)
    except SoftwareFJError as error:
        log.error("Operación no permitida: %s", error)
        mostrar(12, "Operación no permitida: confirmar reserva cancelada", False)

    # 13: demostración de sobrecarga de calcular_costo
    variantes = (
        equipo.calcular_costo(30),
        equipo.calcular_costo(30, con_iva=True),
        equipo.calcular_costo(30, descuento=0.1),
        equipo.calcular_costo(30, con_iva=True, descuento=0.1),
    )
    log.info("Variantes de costo (equipo, 30 h): %s", variantes)
    mostrar(13, f"Sobrecarga de costos (30 h): {variantes}", True)

    # 14: cálculo inconsistente (descuento fuera de rango)
    try:
        equipo.calcular_costo(10, descuento=1.5)
    except SoftwareFJError as error:
        log.error("Cálculo inconsistente: %s", error)
        mostrar(14, "Cálculo inconsistente: descuento 150 %", False)

    # Resumen final (polimorfismo: describir() se comporta distinto en cada clase)
    print("\n--- Resumen ---")
    for servicio in sistema.servicios:
        print(servicio)
    for r in sistema.reservas:
        print(r)
    log.info("=== Fin de la simulación: el sistema siguió activo ===")
    print(f"\nLog generado en: {RUTA_LOG}")


if __name__ == "__main__":
    main()
