"""Clase Reserva: integra cliente, servicio, duración y estado."""

from datetime import datetime
from enum import Enum

from software_fj.cliente import Cliente
from software_fj.entidad_base import EntidadBase
from software_fj.excepciones import (
    ErrorSoftwareFJ,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
)
from software_fj.registro_logs import obtener_logger
from software_fj.servicios.servicio import Servicio

logger = obtener_logger("reservas")  # Los eventos de reservas van al mismo log


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente.

    Flujo: PENDIENTE -> CONFIRMADA -> PROCESADA, o PENDIENTE/CONFIRMADA -> CANCELADA.
    """

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion, **opciones):
        super().__init__()                     # Id automático heredado de EntidadBase
        try:
            if not isinstance(cliente, Cliente):
                raise ReservaInvalidaError("La reserva requiere un cliente válido.")
            if not isinstance(servicio, Servicio):
                raise ReservaInvalidaError("La reserva requiere un servicio válido.")
            # El servicio valida su propia duración y opciones (polimorfismo)
            servicio.validar_parametros(duracion, **opciones)
        except ErrorSoftwareFJ as error:
            logger.error("No se pudo crear la reserva: %s", error)
            raise
        except (TypeError, ValueError) as error:
            # Error inesperado: se encadena a una excepción propia
            logger.error("Error inesperado creando reserva: %r", error)
            raise ReservaInvalidaError(
                "No fue posible crear la reserva con los datos entregados.") from error
        else:
            # Solo se asignan los datos si TODAS las validaciones pasaron
            self._cliente = cliente
            self._servicio = servicio
            self._duracion = duracion
            self._opciones = opciones
            self._estado = EstadoReserva.PENDIENTE
            self._costo_total = None
            self._creada_en = datetime.now()
            logger.info("Reserva %s creada (cliente %s, servicio %s, duración %s %s).",
                        self.id, cliente.id, servicio.id, duracion, servicio.UNIDAD_DURACION)

    # ------------------------- propiedades de solo lectura -------------------------
    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self):
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    # ------------------------------- operaciones -----------------------------------
    def confirmar(self) -> None:
        """PENDIENTE -> CONFIRMADA (el servicio debe seguir disponible)."""
        try:
            if self._estado is not EstadoReserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar una reserva en estado {self._estado.value}.")
            self._servicio.verificar_disponibilidad()
        except ErrorSoftwareFJ as error:
            logger.warning("Confirmación rechazada en %s: %s", self.id, error)
            raise
        else:
            self._estado = EstadoReserva.CONFIRMADA
            logger.info("Reserva %s confirmada.", self.id)
        finally:
            logger.debug("Fin del intento de confirmar la reserva %s", self.id)

    def cancelar(self, motivo: str = "sin motivo") -> None:
        """PENDIENTE o CONFIRMADA -> CANCELADA."""
        try:
            if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva en estado {self._estado.value}.")
        except ErrorSoftwareFJ as error:
            logger.warning("Cancelación rechazada en %s: %s", self.id, error)
            raise
        else:
            self._estado = EstadoReserva.CANCELADA
            logger.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)
        finally:
            logger.debug("Fin del intento de cancelar la reserva %s", self.id)

    def procesar(self, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """CONFIRMADA -> PROCESADA: calcula y guarda el costo total."""
        try:
            if self._estado is not EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas CONFIRMADAS (estado actual: "
                    f"{self._estado.value}).")
            total = self._servicio.calcular_costo(
                self._duracion, impuesto=impuesto, descuento=descuento, **self._opciones)
        except OperacionNoPermitidaError as error:
            logger.warning("Procesamiento rechazado en %s: %s", self.id, error)
            raise
        except ErrorSoftwareFJ as error:
            # Falla del cálculo: la reserva sigue CONFIRMADA y el error se encadena
            logger.error("Falló el cálculo de la reserva %s: %s", self.id, error)
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva {self.id}.") from error
        else:
            self._costo_total = total
            self._estado = EstadoReserva.PROCESADA
            logger.info("Reserva %s procesada. Total: %.2f", self.id, total)
            return total
        finally:
            logger.debug("Fin del intento de procesar la reserva %s", self.id)

    # ---------------------- contrato de EntidadBase -------------------------------
    def validar_datos(self) -> None:
        """Verifica que la reserva mantenga datos coherentes."""
        if not isinstance(self._estado, EstadoReserva):
            raise ReservaInvalidaError("Estado de reserva inválido.")
        self._servicio.validar_parametros(self._duracion, **self._opciones)

    def describir(self) -> str:
        total = f", total ${self._costo_total:,.2f}" if self._costo_total else ""
        return (f"[Reserva] {self.id} - cliente {self._cliente.id}, "
                f"servicio '{self._servicio.nombre}', {self._duracion} "
                f"{self._servicio.UNIDAD_DURACION}, estado {self._estado.value}{total}.")
