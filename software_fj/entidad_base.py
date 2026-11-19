from abc import ABC, abstractmethod
import itertools

class EntidadBase(ABC):
    """
    Clase abstracta que representa las entidades generales del sistema.
    Versión final implementada por el Integrante 2.
    """
    
    # Generador de consecutivos para ids automáticos (ENT-0001, ENT-0002...)
    # itertools.count(1) crea un contador infinito que empieza en 1
    # Es un atributo de clase: se comparte entre TODAS las instancias,
    # así cada entidad nueva obtiene un número distinto y consecutivo
    _contador = itertools.count(1)

    def __init__(self, identificador: str | None = None):
        # Si no se entrega id, se genera uno automático
        # - Si "identificador" tiene un valor (no es None ni vacío), se usa ese
        # - Si no, se genera uno nuevo con next() sobre el contador de la clase,
        #   formateado con 4 dígitos y ceros a la izquierda (ej: ENT-0001)
        self._id = identificador or f"ENT-{next(EntidadBase._contador):04d}"

    @property
    def id(self) -> str:
        """Identificador de solo lectura (encapsulación)."""
        # Al ser una property, permite acceder como "objeto.id"
        # pero no se puede reasignar desde afuera (no hay setter),
        # protegiendo el atributo interno _id
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Obliga a las clases hijas a saber describirse (Método de Kevin)."""
        # Al ser abstracto, cualquier clase hija DEBE implementar este método,
        # si no, Python no dejará instanciarla
        pass
        
    @abstractmethod
    def validar_datos(self) -> None:
        """Obliga a las clases hijas a validar sus propios datos (Tu aporte)."""
        # Igual que el anterior: es un "contrato" que obliga a las clases hijas
        # (como Cliente) a implementar su propia lógica de validación
        pass
