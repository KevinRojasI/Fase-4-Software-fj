"""Punto de entrada del Sistema Integral de Gestión de Software FJ.

Ofrece un menú interactivo por consola para administrar clientes, servicios y
reservas en memoria (sin base de datos). La única persistencia es el archivo
de logs configurado en ``software_fj/registro_logs.py``.

Manejo de errores: cada opción del menú usa ``try / except / else / finally``.
Se capturan las excepciones propias (``ErrorSoftwareFJ`` y sus hijas) y los
errores de entrada (``ValueError``, ``IndexError``...). Todo error se registra
en el log y el programa nunca se detiene por una entrada incorrecta.
"""

from software_fj.cliente import Cliente                                  # Entidad cliente
from software_fj.excepciones import ErrorSoftwareFJ                      # Base de errores propios
from software_fj.registro_logs import obtener_logger                     # Logger a archivo
from software_fj.reserva import Reserva                                  # Reserva (con sus estados)
from software_fj.servicios.alquiler_equipo import AlquilerEquipo         # Servicio por días
from software_fj.servicios.asesoria_especializada import AsesoriaEspecializada  # Por hora y nivel
from software_fj.servicios.reserva_sala import ReservaSala               # Servicio por hora
from software_fj.servicios.servicio import Servicio                      # Clase abstracta base

logger = obtener_logger("main")  # Los eventos del menú quedan en el mismo archivo de logs

# ----------------------------------------------------------------------------
# "Base de datos" en memoria: tres listas que viven mientras corre el programa
# ----------------------------------------------------------------------------
clientes: list[Cliente] = []     # Clientes registrados
servicios: list[Servicio] = []   # Servicios creados (salas, equipos, asesorías)
reservas: list[Reserva] = []     # Reservas realizadas


# ============================================================================
# Utilidades de entrada y de manejo de errores
# ============================================================================
def reportar_error(contexto: str, error: Exception) -> None:
    """Muestra el error al usuario y lo guarda en el archivo de logs."""
    if isinstance(error, ErrorSoftwareFJ):
        # Error propio del dominio (incluye ClienteInvalidoError, que también es ValueError)
        logger.error("%s -> error de dominio: %s", contexto, error)
        print(f"  [X] {error}")
    elif isinstance(error, (ValueError, IndexError)):
        # Error de captura: número mal escrito o posición fuera de la lista
        logger.error("%s -> entrada inválida: %r", contexto, error)
        print(f"  [X] Entrada inválida: {error}")
    else:
        # Cualquier otro error inesperado: se guarda con traza completa
        logger.exception("%s -> error inesperado: %r", contexto, error)
        print(f"  [X] Ocurrió un error inesperado ({type(error).__name__}): {error}")


def pedir_texto(mensaje: str) -> str:
    """Pide un texto por consola y le quita espacios sobrantes."""
    return input(mensaje).strip()


def pedir_entero(mensaje: str) -> int:
    """Pide un entero; si no lo es, ``int()`` lanza ValueError (lo captura quien llama)."""
    return int(input(mensaje).strip())


def pedir_decimal(mensaje: str, por_defecto: float | None = None) -> float:
    """Pide un decimal; si el usuario solo pulsa Enter devuelve ``por_defecto``."""
    texto = input(mensaje).strip().replace(",", ".")   # Acepta coma o punto decimal
    if texto == "" and por_defecto is not None:
        return por_defecto                              # Enter = valor por defecto
    return float(texto)                                 # ValueError si no es número


def seleccionar(lista: list, titulo: str):
    """Muestra una lista numerada y devuelve el elemento elegido.

    Lanza ValueError si no hay elementos o el texto no es un número, e
    IndexError si el número está fuera de rango.
    """
    if not lista:
        raise ValueError(f"No hay {titulo} registrados todavía.")
    print(f"\n--- {titulo.capitalize()} disponibles ---")
    for posicion, elemento in enumerate(lista, start=1):   # Numeración desde 1
        print(f"  {posicion}. {elemento.describir()}")
    posicion = pedir_entero(f"Elija el número de {titulo[:-1] if titulo.endswith('s') else titulo}: ")
    if not 1 <= posicion <= len(lista):
        raise IndexError(f"La posición {posicion} no existe (válidas: 1 a {len(lista)}).")
    return lista[posicion - 1]                              # Convierte a índice base 0


# ============================================================================
# Opción 1: registrar cliente
# ============================================================================
def registrar_cliente() -> None:
    """Pide nombre y correo y crea un Cliente validado."""
    try:
        nombre = pedir_texto("Nombre del cliente: ")
        correo = pedir_texto("Correo del cliente: ")
        cliente = Cliente(nombre, correo)                   # Valida internamente
    except ErrorSoftwareFJ as error:
        reportar_error("Registro de cliente", error)        # Datos inválidos del dominio
    except (ValueError, TypeError, AttributeError) as error:
        reportar_error("Registro de cliente", error)        # Tipos incorrectos u otros fallos
    else:
        clientes.append(cliente)                            # Solo se guarda si todo salió bien
        logger.info("Cliente %s registrado desde el menú.", cliente.id)
        print(f"  [OK] {cliente.describir()}")
    finally:
        logger.debug("Fin del intento de registrar cliente.")


# ============================================================================
# Opción 2: crear servicio (Sala, Equipo o Asesoría)
# ============================================================================
def crear_servicio() -> None:
    """Pide el tipo de servicio y sus datos, y crea el objeto correspondiente."""
    try:
        print("\nTipos de servicio: 1) Sala  2) Equipo  3) Asesoría")
        tipo = pedir_texto("Elija el tipo (1-3): ")
        if tipo not in ("1", "2", "3"):
            raise ValueError(f"Tipo de servicio '{tipo}' no existe (use 1, 2 o 3).")
        nombre = pedir_texto("Nombre del servicio: ")
        tarifa = pedir_decimal("Tarifa base (por hora o por día): ")
        if tipo == "1":                                      # --- Sala ---
            capacidad = pedir_entero("Capacidad (personas): ")
            proyector = pedir_texto("¿Tiene proyector? (s/n): ").lower() == "s"
            servicio = ReservaSala(nombre, tarifa, capacidad, proyector)
        elif tipo == "2":                                    # --- Equipo ---
            tipo_equipo = pedir_texto("Tipo de equipo (ej. portátil): ")
            deposito = pedir_decimal("Depósito de garantía (Enter = 0): ", 0.0)
            servicio = AlquilerEquipo(nombre, tarifa, tipo_equipo, deposito)
        else:                                                # --- Asesoría ---
            especialidad = pedir_texto("Especialidad: ")
            nivel = pedir_texto("Nivel (junior/senior/experto): ")
            servicio = AsesoriaEspecializada(nombre, tarifa, especialidad, nivel)
    except ErrorSoftwareFJ as error:
        reportar_error("Creación de servicio", error)       # Validaciones propias de cada clase
    except (ValueError, TypeError) as error:
        reportar_error("Creación de servicio", error)       # Números mal escritos, etc.
    else:
        servicios.append(servicio)                          # Se guarda solo si se creó bien
        logger.info("Servicio %s creado desde el menú.", servicio.id)
        print(f"  [OK] {servicio.describir()}")
    finally:
        logger.debug("Fin del intento de crear servicio.")


# ============================================================================
# Opción 3: crear reserva
# ============================================================================
def crear_reserva() -> None:
    """Asocia un cliente y un servicio registrados y crea la reserva."""
    try:
        cliente = seleccionar(clientes, "clientes")
        servicio = seleccionar(servicios, "servicios")
        opciones = {}                                        # Opciones propias del servicio
        if isinstance(servicio, AlquilerEquipo):
            duracion = pedir_entero("Días de alquiler (entero): ")    # El equipo exige int
        else:
            duracion = pedir_decimal("Horas (múltiplos de 0.5): ")    # Sala/asesoría: float
        if isinstance(servicio, ReservaSala):
            asistentes = pedir_texto("Asistentes (Enter para omitir): ")
            if asistentes:
                opciones["asistentes"] = int(asistentes)     # ValueError si no es entero
        reserva = Reserva(cliente, servicio, duracion, **opciones)   # Valida en el constructor
    except ErrorSoftwareFJ as error:
        reportar_error("Creación de reserva", error)
    except (ValueError, IndexError, TypeError) as error:
        reportar_error("Creación de reserva", error)
    else:
        reservas.append(reserva)
        print(f"  [OK] {reserva.describir()}")
    finally:
        logger.debug("Fin del intento de crear reserva.")


# ============================================================================
# Opción 4: gestionar reserva (confirmar / cancelar / procesar)
# ============================================================================
def gestionar_reserva() -> None:
    """Permite confirmar, cancelar o procesar una reserva existente."""
    try:
        reserva = seleccionar(reservas, "reservas")
        print("\nAcciones: 1) Confirmar  2) Cancelar  3) Procesar")
        accion = pedir_texto("Elija la acción (1-3): ")
        if accion == "1":
            reserva.confirmar()                              # PENDIENTE -> CONFIRMADA
            mensaje = "Reserva confirmada."
        elif accion == "2":
            motivo = pedir_texto("Motivo (Enter = sin motivo): ") or "sin motivo"
            reserva.cancelar(motivo)                         # -> CANCELADA
            mensaje = "Reserva cancelada."
        elif accion == "3":
            impuesto = pedir_decimal("Impuesto entre 0 y 1, ej. 0.19 (Enter = 0): ", 0.0)
            descuento = pedir_decimal("Descuento entre 0 y 0.9 (Enter = 0): ", 0.0)
            total = reserva.procesar(impuesto, descuento)    # CONFIRMADA -> PROCESADA
            mensaje = f"Reserva procesada. Total: ${total:,.2f}"
        else:
            raise ValueError(f"Acción '{accion}' no existe (use 1, 2 o 3).")
    except ErrorSoftwareFJ as error:
        reportar_error("Gestión de reserva", error)         # Ej.: operación no permitida
    except (ValueError, IndexError) as error:
        reportar_error("Gestión de reserva", error)
    else:
        print(f"  [OK] {mensaje}")
    finally:
        logger.debug("Fin del intento de gestionar reserva.")


# ============================================================================
# Opción 5: listar todo lo que hay en memoria
# ============================================================================
def listar_todo() -> None:
    """Imprime clientes, servicios y reservas actuales."""
    try:
        for titulo, coleccion in (("CLIENTES", clientes),
                                  ("SERVICIOS", servicios),
                                  ("RESERVAS", reservas)):
            print(f"\n=== {titulo} ({len(coleccion)}) ===")
            if not coleccion:
                print("  (sin registros)")
            for elemento in coleccion:
                print(f"  - {elemento.describir()}")
    except Exception as error:                               # Respaldo: listar nunca debe tumbar el menú
        reportar_error("Listado", error)
    else:
        logger.info("Listado: %d clientes, %d servicios, %d reservas.",
                    len(clientes), len(servicios), len(reservas))
    finally:
        logger.debug("Fin del listado.")


# ============================================================================
# Opción 6: simulación automática (más de 10 operaciones, sin detenerse)
# ============================================================================
def _intentar(numero: int, descripcion: str, accion) -> object:
    """Ejecuta una operación de la simulación sin que un error la detenga.

    Devuelve lo que retorne ``accion`` o ``None`` si falló. Cada resultado
    (éxito o rechazo) se imprime y se registra en el log.
    """
    resultado = None
    try:
        resultado = accion()                                 # Ejecuta la operación
    except ErrorSoftwareFJ as error:
        logger.warning("[SIM %02d] %s -> rechazada: %s", numero, descripcion, error)
        print(f"  [{numero:02d}] [RECHAZADA] {descripcion}\n         Motivo: {error}")
    except (ValueError, TypeError, AttributeError, IndexError) as error:
        logger.error("[SIM %02d] %s -> error de entrada: %r", numero, descripcion, error)
        print(f"  [{numero:02d}] [RECHAZADA] {descripcion}\n         Motivo: {error!r}")
    else:
        logger.info("[SIM %02d] %s -> OK", numero, descripcion)
        print(f"  [{numero:02d}] [OK]        {descripcion}")
    finally:
        logger.debug("[SIM %02d] fin de la operación.", numero)
    return resultado


def _guardar(lista: list, objeto):
    """Agrega ``objeto`` a ``lista`` y lo devuelve (útil dentro de lambdas)."""
    lista.append(objeto)
    return objeto


def ejecutar_simulacion() -> None:
    """Ejecuta 16 operaciones mezclando casos válidos e inválidos."""
    print("\n########## SIMULACIÓN AUTOMÁTICA ##########")
    logger.info("Inicio de la simulación automática.")
    try:
        # ---- Clientes (1-4): dos válidos y dos inválidos -------------------
        ana = _intentar(1, "Cliente válido: Ana Torres",
                        lambda: _guardar(clientes, Cliente("Ana Torres", "ana.torres@correo.com")))
        _intentar(2, "Cliente inválido: correo sin '@'",
                  lambda: _guardar(clientes, Cliente("Pedro Gómez", "pedro-correo.com")))
        _intentar(3, "Cliente inválido: nombre vacío",
                  lambda: _guardar(clientes, Cliente("   ", "vacio@correo.com")))
        _intentar(4, "Cliente válido: Luis Pérez",
                  lambda: _guardar(clientes, Cliente("Luis Pérez", "luis.perez@correo.com")))

        # ---- Servicios (5-9): tres válidos y dos inválidos -----------------
        sala = _intentar(5, "Servicio válido: Sala Andes (10 personas, proyector)",
                         lambda: _guardar(servicios, ReservaSala("Sala Andes", 40000, 10, True)))
        _intentar(6, "Servicio inválido: sala con capacidad negativa",
                  lambda: _guardar(servicios, ReservaSala("Sala Rota", 40000, -5)))
        equipo = _intentar(7, "Servicio válido: Portátil Dell por día",
                           lambda: _guardar(servicios, AlquilerEquipo("Portátil Dell", 25000, "portátil", 100000)))
        _intentar(8, "Servicio inválido: asesoría con nivel 'maestro'",
                  lambda: _guardar(servicios, AsesoriaEspecializada("Asesoría Cloud", 80000, "Cloud", "maestro")))
        asesoria = _intentar(9, "Servicio válido: asesoría de seguridad nivel senior",
                             lambda: _guardar(servicios, AsesoriaEspecializada("Asesoría M365", 80000, "Seguridad", "senior")))

        # ---- Reservas (10-16): éxitos y fallos de distinto tipo -----------
        def flujo_sala() -> Reserva:
            """Crea, confirma y procesa una reserva de sala con IVA."""
            reserva = _guardar(reservas, Reserva(ana, sala, 2, asistentes=8))
            reserva.confirmar()
            reserva.procesar(impuesto=0.19)                  # (40000+15000)*2*1.19 = 130 900
            return reserva
        _intentar(10, "Reserva exitosa de sala (2 h, 8 asistentes) confirmada y procesada", flujo_sala)

        _intentar(11, "Reserva fallida: 50 asistentes superan la capacidad de la sala",
                  lambda: _guardar(reservas, Reserva(ana, sala, 2, asistentes=50)))

        def flujo_equipo() -> Reserva:
            """Alquiler de 8 días: aplica el descuento semanal + descuento y IVA."""
            reserva = _guardar(reservas, Reserva(ana, equipo, 8))
            reserva.confirmar()
            reserva.procesar(impuesto=0.19, descuento=0.05)
            return reserva
        _intentar(12, "Reserva exitosa de equipo (8 días, descuento semanal)", flujo_equipo)

        _intentar(13, "Reserva fallida: alquiler de 45 días (máximo 30)",
                  lambda: _guardar(reservas, Reserva(ana, equipo, 45)))

        def flujo_cancelada() -> Reserva:
            """Confirma una asesoría y la cancela (flujo válido)."""
            reserva = _guardar(reservas, Reserva(clientes[-1], asesoria, 2.5))
            reserva.confirmar()
            reserva.cancelar("el cliente cambió de planes")
            return reserva
        cancelada = _intentar(14, "Reserva de asesoría (2.5 h) confirmada y luego cancelada", flujo_cancelada)

        _intentar(15, "Operación no permitida: procesar una reserva ya CANCELADA",
                  lambda: cancelada.procesar())

        def flujo_no_disponible() -> Reserva:
            """El servicio deja de estar disponible antes de confirmar."""
            reserva = _guardar(reservas, Reserva(ana, sala, 1))
            sala.marcar_no_disponible()                      # Simula un servicio fuera de servicio
            try:
                reserva.confirmar()                          # Debe lanzar ServicioNoDisponibleError
            finally:
                sala.marcar_disponible()                     # Se restablece siempre, falle o no
            return reserva
        _intentar(16, "Confirmación fallida: el servicio no está disponible", flujo_no_disponible)
    except Exception as error:                               # Red de seguridad extra: la simulación no se cae
        reportar_error("Simulación automática", error)
    else:
        print("\n  Simulación terminada: use la opción 5 para ver lo que quedó en memoria.")
    finally:
        logger.info("Fin de la simulación automática.")


# ============================================================================
# Menú principal
# ============================================================================
def mostrar_menu() -> None:
    """Imprime las opciones del menú."""
    print("\n" + "=" * 52)
    print("   SOFTWARE FJ - GESTIÓN DE CLIENTES Y RESERVAS")
    print("=" * 52)
    print("  1. Registrar nuevo cliente")
    print("  2. Crear nuevo servicio (Sala / Equipo / Asesoría)")
    print("  3. Crear una reserva")
    print("  4. Gestionar reserva (confirmar / cancelar / procesar)")
    print("  5. Listar clientes, servicios y reservas")
    print("  6. Ejecutar simulación automática (16 operaciones)")
    print("  7. Salir")


def main() -> None:
    """Bucle principal: el programa solo termina con la opción 7 o Ctrl+C."""
    acciones = {                                             # Opción -> función
        "1": registrar_cliente,
        "2": crear_servicio,
        "3": crear_reserva,
        "4": gestionar_reserva,
        "5": listar_todo,
        "6": ejecutar_simulacion,
    }
    logger.info("Sistema iniciado.")
    while True:
        try:
            mostrar_menu()
            opcion = pedir_texto("Seleccione una opción (1-7): ")
            if opcion == "7":
                break                                        # Salida limpia
            accion = acciones.get(opcion)
            if accion is None:                               # Opción desconocida
                raise ValueError(f"La opción '{opcion}' no existe (use 1 a 7).")
            accion()
        except (KeyboardInterrupt, EOFError):
            print("\n  Entrada interrumpida: cerrando el sistema.")
            logger.warning("Sistema cerrado por interrupción de entrada.")
            break
        except Exception as error:                           # Último respaldo: nunca se cae el menú
            reportar_error("Menú principal", error)
        else:
            logger.debug("Opción %s ejecutada.", opcion)
        finally:
            logger.debug("Fin de una vuelta del menú.")
    logger.info("Sistema finalizado.")
    print("¡Hasta pronto!")


if __name__ == "__main__":
    main()                                                   # Solo corre si se ejecuta directamente
