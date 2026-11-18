"""Demostración de la clase Reserva (Kevin David Rojas Ibarra).

Ejecutar:  python demo_reservas.py
Simula 15 operaciones válidas e inválidas sin detener el programa.
"""

from demo_servicios import ejecutar_operacion
from software_fj.cliente import Cliente
from software_fj.registro_logs import obtener_logger
from software_fj.reserva import Reserva
from software_fj.servicios import ReservaSala

logger = obtener_logger("demo_reservas")


def main() -> None:
    logger.info("===== Inicio de la demostración de reservas =====")

    cliente = ejecutar_operacion(1, "Crear cliente válido",
        lambda: Cliente("Ana Pérez", "ana@correo.com"))
    ejecutar_operacion(2, "Crear cliente con correo sin @ (inválido)",
        lambda: Cliente("Luis Gómez", "luiscorreo.com"))
    sala = ejecutar_operacion(3, "Crear sala válida",
        lambda: ReservaSala("Sala Innovación", 80000, capacidad=10, tiene_proyector=True))

    reserva = ejecutar_operacion(4, "Crear reserva válida (3 h, 5 asistentes)",
        lambda: Reserva(cliente, sala, 3, asistentes=5))
    ejecutar_operacion(5, "Crear reserva sin cliente (None)",
        lambda: Reserva(None, sala, 3))
    ejecutar_operacion(6, "Crear reserva con duración de 20 h (inválida)",
        lambda: Reserva(cliente, sala, 20))

    if reserva:
        ejecutar_operacion(7, "Procesar reserva sin confirmar",
            lambda: reserva.procesar())
        ejecutar_operacion(8, "Confirmar reserva", lambda: reserva.confirmar())
        ejecutar_operacion(9, "Confirmar de nuevo la misma reserva",
            lambda: reserva.confirmar())
        ejecutar_operacion(10, "Procesar reserva con IVA 19 %",
            lambda: reserva.procesar(impuesto=0.19))
        ejecutar_operacion(11, "Cancelar una reserva ya procesada",
            lambda: reserva.cancelar("cambio de planes"))
        print("\n" + reserva.describir())

    if cliente and sala:
        otra = ejecutar_operacion(12, "Crear y cancelar una reserva pendiente",
            lambda: Reserva(cliente, sala, 2))
        if otra:
            otra.cancelar("el cliente ya no la necesita")
            ejecutar_operacion(13, "Procesar una reserva cancelada",
                lambda: otra.procesar())
        sala.marcar_no_disponible()
        pendiente = ejecutar_operacion(14, "Crear reserva con la sala aún válida",
            lambda: Reserva(cliente, sala, 1))
        if pendiente:
            ejecutar_operacion(15, "Confirmar con la sala NO disponible",
                lambda: pendiente.confirmar())

    logger.info("===== Fin de la demostración de reservas =====")
    print("\nDemostración terminada. Revise logs/software_fj.log")


if __name__ == "__main__":
    main()
