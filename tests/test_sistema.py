"""Pruebas unitarias (unittest) del Sistema Integral de Software FJ.

Cubre: excepciones, logs, Cliente, los tres servicios (con cálculo polimórfico
de costos, impuestos y descuentos) y el flujo completo de Reserva.

Ejecución desde la raíz del proyecto:
    python -m unittest discover -s tests -t . -v
"""

import logging          # Para verificar el logger del sistema
import unittest         # Librería estándar de pruebas

from software_fj.cliente import Cliente
from software_fj.entidad_base import EntidadBase
from software_fj.excepciones import (
    CalculoInconsistenteError, ClienteInvalidoError, ErrorSoftwareFJ,
    OperacionNoPermitidaError, ParametroInvalidoError, ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from software_fj.registro_logs import obtener_logger
from software_fj.reserva import EstadoReserva, Reserva
from software_fj.servicios.alquiler_equipo import AlquilerEquipo
from software_fj.servicios.asesoria_especializada import AsesoriaEspecializada
from software_fj.servicios.reserva_sala import ReservaSala
from software_fj.servicios.servicio import Servicio


# ============================================================================
# Excepciones y logs
# ============================================================================
class TestExcepcionesYLogs(unittest.TestCase):
    """Verifica códigos, jerarquía de excepciones y el logger."""

    def test_codigos_de_error(self):
        """Cada excepción propia debe exponer su código SFJ-00X."""
        esperados = {ParametroInvalidoError: "SFJ-001", ServicioNoDisponibleError: "SFJ-002",
                     CalculoInconsistenteError: "SFJ-003", ClienteInvalidoError: "SFJ-004",
                     ReservaInvalidaError: "SFJ-005", OperacionNoPermitidaError: "SFJ-006"}
        for clase, codigo in esperados.items():
            with self.subTest(clase=clase.__name__):          # Un subtest por excepción
                self.assertEqual(clase("msg").codigo, codigo)

    def test_formato_str(self):
        """__str__ debe producir '[CODIGO] mensaje'."""
        self.assertEqual(str(ParametroInvalidoError("dato malo")), "[SFJ-001] dato malo")

    def test_jerarquia(self):
        """Todas heredan de ErrorSoftwareFJ; ClienteInvalidoError también de ValueError."""
        for clase in (ParametroInvalidoError, ServicioNoDisponibleError, CalculoInconsistenteError,
                      ClienteInvalidoError, ReservaInvalidaError, OperacionNoPermitidaError):
            self.assertTrue(issubclass(clase, ErrorSoftwareFJ))
        self.assertTrue(issubclass(ClienteInvalidoError, ValueError))

    def test_logger_por_modulo(self):
        """El sub-logger cuelga del logger base 'software_fj' y este tiene handlers."""
        log = obtener_logger("pruebas")
        self.assertIsInstance(log, logging.Logger)
        self.assertEqual(log.name, "software_fj.pruebas")
        self.assertTrue(log.parent.handlers)                  # Archivo (o consola de respaldo)


# ============================================================================
# Cliente
# ============================================================================
class TestCliente(unittest.TestCase):
    """Creación válida e inválida de clientes."""

    def test_creacion_exitosa(self):
        """Un cliente con datos correctos se crea y se describe."""
        cliente = Cliente("Ana Torres", "ana@correo.com")
        self.assertEqual(cliente.nombre, "Ana Torres")
        self.assertTrue(cliente.id.startswith("ENT-"))
        self.assertIn("Ana Torres", cliente.describir())
        cliente.validar_datos()                               # No debe lanzar nada

    def test_ids_unicos(self):
        """Dos clientes nunca comparten identificador."""
        self.assertNotEqual(Cliente("Ana", "a@b.co").id, Cliente("Luis", "l@b.co").id)

    def test_identificador_explicito(self):
        """Si se entrega un id, se respeta."""
        self.assertEqual(Cliente("Ana", "a@b.co", "CLI-1").id, "CLI-1")

    def test_nombre_invalido(self):
        """Nombre vacío, solo espacios o None lanzan ClienteInvalidoError."""
        for nombre in ("", "   ", None):
            with self.subTest(nombre=nombre):
                with self.assertRaises(ClienteInvalidoError):
                    Cliente(nombre, "ana@correo.com")

    def test_correo_invalido(self):
        """Correo vacío, sin '@' o sin '.' lanzan ClienteInvalidoError."""
        for correo in ("", None, "sin-arroba.com", "ana@correo"):
            with self.subTest(correo=correo):
                with self.assertRaises(ClienteInvalidoError):
                    Cliente("Ana", correo)

    def test_error_compatible_con_valueerror(self):
        """El error de cliente también se captura como ValueError y trae su código."""
        with self.assertRaises(ValueError) as contexto:
            Cliente("", "a@b.co")
        self.assertEqual(contexto.exception.codigo, "SFJ-004")

    def test_entidad_base_es_abstracta(self):
        """EntidadBase no se puede instanciar directamente."""
        with self.assertRaises(TypeError):
            EntidadBase()


# ============================================================================
# ReservaSala
# ============================================================================
class TestReservaSala(unittest.TestCase):
    """Cálculo y validaciones de la sala de reuniones."""

    def setUp(self):
        """Una sala con proyector y otra sin él para cada prueba."""
        self.con_proyector = ReservaSala("Sala Andes", 20000, 10, True)
        self.sin_proyector = ReservaSala("Sala Sencilla", 20000, 10)

    def test_creacion_y_propiedades(self):
        self.assertEqual(self.con_proyector.capacidad, 10)
        self.assertTrue(self.con_proyector.tiene_proyector)
        self.assertTrue(self.con_proyector.disponible)
        self.assertIn("con proyector", self.con_proyector.describir())

    def test_costo_base(self):
        """Sin proyector: 20000*2; con proyector: (20000+15000)*2."""
        self.assertAlmostEqual(self.sin_proyector.calcular_costo_base(2), 40000)
        self.assertAlmostEqual(self.con_proyector.calcular_costo_base(2), 70000)

    def test_costo_con_impuesto_y_descuento(self):
        """Fórmula: base * (1 - descuento) * (1 + impuesto)."""
        self.assertAlmostEqual(self.con_proyector.calcular_costo(2, impuesto=0.19), 83300)
        self.assertAlmostEqual(self.con_proyector.calcular_costo(2, descuento=0.10), 63000)
        self.assertAlmostEqual(
            self.con_proyector.calcular_costo(2, impuesto=0.19, descuento=0.10), 74970)

    def test_variantes_de_calculo(self):
        """Las variantes 'sobrecargadas' llaman a calcular_costo."""
        self.assertAlmostEqual(self.con_proyector.calcular_costo_con_impuesto(2), 83300)  # IVA 19 %
        self.assertAlmostEqual(
            self.con_proyector.calcular_costo_con_descuento(2, 0.10, impuesto=0.19), 74970)

    def test_duraciones_invalidas(self):
        """Fuera de rango, no múltiplo de 0.5, texto o bool son inválidos."""
        for duracion in (0, -1, 12.5, 1.3, "2", True, None, float("nan")):
            with self.subTest(duracion=duracion):
                with self.assertRaises(ParametroInvalidoError):
                    self.sin_proyector.validar_parametros(duracion)

    def test_duracion_minima_valida(self):
        self.assertAlmostEqual(self.sin_proyector.calcular_costo(0.5), 10000)

    def test_asistentes(self):
        """Los asistentes no pueden superar la capacidad ni ser inválidos."""
        self.sin_proyector.validar_parametros(2, asistentes=10)   # En el límite: válido
        for asistentes in (11, 0, -3, "5", True):
            with self.subTest(asistentes=asistentes):
                with self.assertRaises(ParametroInvalidoError):
                    self.sin_proyector.validar_parametros(2, asistentes=asistentes)

    def test_datos_invalidos_en_constructor(self):
        """Nombre corto, tarifa no positiva o capacidad inválida lanzan error."""
        with self.assertRaises(ParametroInvalidoError):
            ReservaSala("ab", 1000, 5)
        for tarifa in (0, -10, "100", None):
            with self.subTest(tarifa=tarifa):
                with self.assertRaises(ParametroInvalidoError):
                    ReservaSala("Sala X", tarifa, 5)
        for capacidad in (0, -1, 2.5, True):
            with self.subTest(capacidad=capacidad):
                with self.assertRaises(ParametroInvalidoError):
                    ReservaSala("Sala X", 1000, capacidad)

    def test_porcentajes_invalidos(self):
        """Impuesto > 1 o descuento > 0.9 se rechazan."""
        with self.assertRaises(ParametroInvalidoError):
            self.sin_proyector.calcular_costo(2, impuesto=1.5)
        with self.assertRaises(ParametroInvalidoError):
            self.sin_proyector.calcular_costo(2, descuento=0.95)

    def test_servicio_no_disponible(self):
        """Un servicio no disponible no puede calcular costos."""
        self.sin_proyector.marcar_no_disponible()
        with self.assertRaises(ServicioNoDisponibleError):
            self.sin_proyector.calcular_costo(2)
        self.sin_proyector.marcar_disponible()
        self.assertAlmostEqual(self.sin_proyector.calcular_costo(2), 40000)


# ============================================================================
# AlquilerEquipo
# ============================================================================
class TestAlquilerEquipo(unittest.TestCase):
    """Alquiler por días con descuento semanal."""

    def setUp(self):
        self.equipo = AlquilerEquipo("Portátil Dell", 50000, "portátil", 100000)

    def test_creacion(self):
        self.assertEqual(self.equipo.tipo_equipo, "portátil")
        self.assertEqual(self.equipo.deposito_garantia, 100000.0)
        self.assertIn("depósito", self.equipo.describir())

    def test_costo_sin_descuento_semanal(self):
        """Con 6 días no aplica el 10 %."""
        self.assertAlmostEqual(self.equipo.calcular_costo_base(6), 300000)

    def test_costo_con_descuento_semanal(self):
        """Desde 7 días se descuenta el 10 %."""
        self.assertAlmostEqual(self.equipo.calcular_costo_base(7), 315000)

    def test_costo_total_con_impuesto_y_descuento(self):
        """315000 * 0.9 * 1.19 = 337 365."""
        self.assertAlmostEqual(
            self.equipo.calcular_costo(7, impuesto=0.19, descuento=0.10), 337365)

    def test_dias_invalidos(self):
        """Solo enteros entre 1 y 30."""
        for dias in (0, 31, -2, 2.5, "3", True):
            with self.subTest(dias=dias):
                with self.assertRaises(ParametroInvalidoError):
                    self.equipo.validar_parametros(dias)

    def test_datos_invalidos_en_constructor(self):
        with self.assertRaises(ParametroInvalidoError):
            AlquilerEquipo("Portátil", 50000, "   ")              # Tipo vacío
        with self.assertRaises(ParametroInvalidoError):
            AlquilerEquipo("Portátil", 50000, "pc", -1)           # Depósito negativo
        with self.assertRaises(ParametroInvalidoError):
            AlquilerEquipo("Portátil", 50000, "pc", True)         # Depósito booleano


# ============================================================================
# AsesoriaEspecializada
# ============================================================================
class TestAsesoriaEspecializada(unittest.TestCase):
    """Asesoría por hora con multiplicador según el nivel."""

    def test_costo_por_nivel(self):
        """junior x1.0, senior x1.5, experto x2.0."""
        casos = (("junior", 1, 60000), ("senior", 2, 180000), ("experto", 3.5, 420000))
        for nivel, horas, esperado in casos:
            with self.subTest(nivel=nivel):
                asesoria = AsesoriaEspecializada("Asesoría M365", 60000, "Seguridad", nivel)
                self.assertAlmostEqual(asesoria.calcular_costo_base(horas), esperado)

    def test_nivel_no_distingue_mayusculas(self):
        asesoria = AsesoriaEspecializada("Asesoría M365", 60000, "Seguridad", " SENIOR ")
        self.assertEqual(asesoria.nivel, "senior")
        self.assertIn("senior", asesoria.describir())

    def test_costo_total_con_impuesto(self):
        """60000 * 1.5 * 2 * 1.19 = 214 200."""
        asesoria = AsesoriaEspecializada("Asesoría M365", 60000, "Seguridad", "senior")
        self.assertAlmostEqual(asesoria.calcular_costo(2, impuesto=0.19), 214200)

    def test_datos_invalidos_en_constructor(self):
        with self.assertRaises(ParametroInvalidoError):
            AsesoriaEspecializada("Asesoría", 60000, "Cloud", "maestro")   # Nivel inexistente
        with self.assertRaises(ParametroInvalidoError):
            AsesoriaEspecializada("Asesoría", 60000, "ab")                 # Especialidad corta
        with self.assertRaises(ParametroInvalidoError):
            AsesoriaEspecializada("Asesoría", 60000, "Cloud", 5)           # Nivel no texto

    def test_duraciones_invalidas(self):
        """Entre 1 y 8 horas, en múltiplos de 0.5."""
        asesoria = AsesoriaEspecializada("Asesoría", 60000, "Cloud")
        for horas in (0.5, 9, 1.3, 0, "2", True):
            with self.subTest(horas=horas):
                with self.assertRaises(ParametroInvalidoError):
                    asesoria.validar_parametros(horas)
        asesoria.validar_parametros(1.5)                                   # Válida


# ============================================================================
# Polimorfismo
# ============================================================================
class TestPolimorfismo(unittest.TestCase):
    """Los tres servicios se usan igual a través de la clase Servicio."""

    def test_servicio_es_abstracto(self):
        with self.assertRaises(TypeError):
            Servicio("Servicio", 1000)

    def test_misma_interfaz_distinto_resultado(self):
        """calcular_costo y describir funcionan igual en todas las hijas."""
        servicios = [(ReservaSala("Sala Andes", 20000, 10, True), 2),
                     (AlquilerEquipo("Portátil", 50000, "pc"), 7),
                     (AsesoriaEspecializada("Asesoría", 60000, "Cloud", "experto"), 2)]
        for servicio, duracion in servicios:
            with self.subTest(servicio=type(servicio).__name__):
                self.assertIsInstance(servicio, Servicio)
                self.assertIsInstance(servicio, EntidadBase)
                self.assertGreater(servicio.calcular_costo(duracion, impuesto=0.19), 0)
                self.assertIsInstance(servicio.describir(), str)
                servicio.validar_datos()                     # Contrato de EntidadBase


# ============================================================================
# Reserva (flujo completo)
# ============================================================================
class TestReserva(unittest.TestCase):
    """PENDIENTE -> CONFIRMADA -> PROCESADA, o -> CANCELADA."""

    def setUp(self):
        """Cliente y sala (20000/h, sin proyector) reutilizados en cada prueba."""
        self.cliente = Cliente("Ana Torres", "ana@correo.com")
        self.sala = ReservaSala("Sala Andes", 20000, 10)
        self.reserva = Reserva(self.cliente, self.sala, 2, asistentes=8)

    def test_creacion(self):
        """Nace PENDIENTE y sin costo."""
        self.assertEqual(self.reserva.estado, EstadoReserva.PENDIENTE)
        self.assertIsNone(self.reserva.costo_total)
        self.assertIs(self.reserva.cliente, self.cliente)
        self.assertIs(self.reserva.servicio, self.sala)
        self.assertEqual(self.reserva.duracion, 2)
        self.reserva.validar_datos()
        self.assertIn("PENDIENTE", self.reserva.describir())

    def test_flujo_confirmar_y_procesar(self):
        """Confirmar y procesar: 20000*2*1.19 = 47 600."""
        self.reserva.confirmar()
        self.assertEqual(self.reserva.estado, EstadoReserva.CONFIRMADA)
        total = self.reserva.procesar(impuesto=0.19)
        self.assertAlmostEqual(total, 47600)
        self.assertEqual(self.reserva.estado, EstadoReserva.PROCESADA)
        self.assertAlmostEqual(self.reserva.costo_total, 47600)
        self.assertIn("PROCESADA", self.reserva.describir())

    def test_cancelar_desde_pendiente_y_confirmada(self):
        self.reserva.cancelar("cambio de planes")
        self.assertEqual(self.reserva.estado, EstadoReserva.CANCELADA)
        otra = Reserva(self.cliente, self.sala, 1)
        otra.confirmar()
        otra.cancelar()
        self.assertEqual(otra.estado, EstadoReserva.CANCELADA)

    def test_operaciones_no_permitidas(self):
        """Transiciones inválidas lanzan OperacionNoPermitidaError."""
        with self.assertRaises(OperacionNoPermitidaError):     # Procesar sin confirmar
            self.reserva.procesar()
        self.reserva.confirmar()
        with self.assertRaises(OperacionNoPermitidaError):     # Confirmar dos veces
            self.reserva.confirmar()
        self.reserva.procesar()
        with self.assertRaises(OperacionNoPermitidaError):     # Cancelar una procesada
            self.reserva.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):     # Procesar dos veces
            self.reserva.procesar()

    def test_reserva_cancelada_no_se_reactiva(self):
        self.reserva.cancelar()
        for operacion in (self.reserva.confirmar, self.reserva.cancelar, self.reserva.procesar):
            with self.subTest(operacion=operacion.__name__):
                with self.assertRaises(OperacionNoPermitidaError):
                    operacion()
        self.assertEqual(self.reserva.estado, EstadoReserva.CANCELADA)

    def test_confirmar_con_servicio_no_disponible(self):
        """Falla y la reserva sigue PENDIENTE."""
        self.sala.marcar_no_disponible()
        with self.assertRaises(ServicioNoDisponibleError):
            self.reserva.confirmar()
        self.assertEqual(self.reserva.estado, EstadoReserva.PENDIENTE)

    def test_procesar_con_servicio_no_disponible_encadena_error(self):
        """ReservaInvalidaError conserva la causa original (raise ... from)."""
        self.reserva.confirmar()
        self.sala.marcar_no_disponible()
        with self.assertRaises(ReservaInvalidaError) as contexto:
            self.reserva.procesar()
        self.assertIsInstance(contexto.exception.__cause__, ServicioNoDisponibleError)
        self.assertEqual(self.reserva.estado, EstadoReserva.CONFIRMADA)   # No cambió
        self.assertIsNone(self.reserva.costo_total)

    def test_procesar_con_impuesto_invalido(self):
        """Un impuesto fuera de rango no deja la reserva a medias."""
        self.reserva.confirmar()
        with self.assertRaises(ReservaInvalidaError) as contexto:
            self.reserva.procesar(impuesto=5)
        self.assertIsInstance(contexto.exception.__cause__, ParametroInvalidoError)
        self.assertEqual(self.reserva.estado, EstadoReserva.CONFIRMADA)

    def test_creacion_con_datos_invalidos(self):
        """Cliente o servicio inválidos -> ReservaInvalidaError; duración mala -> ParametroInvalidoError."""
        with self.assertRaises(ReservaInvalidaError):
            Reserva("no soy cliente", self.sala, 2)
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, "no soy servicio", 2)
        with self.assertRaises(ParametroInvalidoError):
            Reserva(self.cliente, self.sala, 99)
        with self.assertRaises(ParametroInvalidoError):
            Reserva(self.cliente, self.sala, 2, asistentes=500)

    def test_reservas_con_los_tres_servicios(self):
        """El flujo completo funciona igual con equipo y asesoría (polimorfismo)."""
        equipo = AlquilerEquipo("Portátil", 50000, "pc")
        asesoria = AsesoriaEspecializada("Asesoría", 60000, "Cloud", "senior")
        casos = ((equipo, 7, 315000), (asesoria, 2, 180000))
        for servicio, duracion, esperado in casos:
            with self.subTest(servicio=type(servicio).__name__):
                reserva = Reserva(self.cliente, servicio, duracion)
                reserva.confirmar()
                self.assertAlmostEqual(reserva.procesar(), esperado)
                self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)


if __name__ == "__main__":
    unittest.main(verbosity=2)                                 # Permite ejecutar el archivo directamente
