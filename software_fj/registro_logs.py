"""Configuración del archivo de logs (única persistencia permitida)."""

import logging
from pathlib import Path

# Carpeta logs/ en la raíz del proyecto y archivo donde se guardan los eventos
# __file__ es la ruta de este archivo; .resolve() la convierte en absoluta
# .parent.parent sube dos niveles (de este archivo a la raíz del proyecto)
RUTA_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARCHIVO_LOG = RUTA_LOGS / "software_fj.log"


def _configurar_logger_base() -> logging.Logger:
    """Crea (una sola vez) el logger principal con salida a archivo."""
    # Se obtiene (o crea) el logger con nombre "software_fj"
    base = logging.getLogger("software_fj")
    if not base.handlers:  # Evita duplicar handlers si se llama varias veces
        # Nivel DEBUG: captura todos los mensajes, desde los más detallados
        base.setLevel(logging.DEBUG)
        try:
            RUTA_LOGS.mkdir(parents=True, exist_ok=True)       # Crea logs/ si no existe
            # Handler que escribe los logs en el archivo definido arriba
            handler = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        except OSError:
            # Si no se puede escribir el archivo, el sistema sigue vivo usando consola
            # (por ejemplo, si no hay permisos o la ruta no es válida)
            handler = logging.StreamHandler()

        # Define el formato de cada línea de log:
        # fecha/hora | nivel (INFO, ERROR, etc.) | nombre del logger | mensaje
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        base.addHandler(handler)

        # Evita que los mensajes se dupliquen subiendo a loggers padre (como el root)
        base.propagate = False
    return base


def obtener_logger(modulo: str = "") -> logging.Logger:
    """Devuelve el logger del sistema o un sub-logger por módulo."""
    # Se asegura de que el logger base ya esté configurado
    base = _configurar_logger_base()
    # Si se especifica un módulo, se devuelve un logger "hijo" (ej: software_fj.cliente)
    # para poder identificar de qué parte del sistema viene cada mensaje;
    # si no se especifica, se devuelve el logger base tal cual
    return base.getChild(modulo) if modulo else base
