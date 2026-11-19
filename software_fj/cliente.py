from software_fj.entidad_base import EntidadBase
from software_fj.excepciones import ClienteInvalidoError

class Cliente(EntidadBase):
    """
    Clase Cliente que hereda de EntidadBase.
    Implementa la validación de datos usando excepciones para garantizar robustez.
    """
    
    def __init__(self, nombre: str, correo: str, identificador: str | None = None):
        # Llamamos al constructor de la clase padre (EntidadBase),
        # pasándole el identificador para que lo gestione ella
        super().__init__(identificador)
        
        # Guardamos el nombre recibido como atributo del cliente
        self.nombre = nombre
        
        # Guardamos el correo recibido como atributo del cliente
        self.correo = correo
        
        # Validamos los datos justo después de asignarlos.
        # Si algo está mal, aquí mismo se lanzará la excepción
        # y el objeto Cliente nunca llegará a crearse con datos inválidos
        self.validar_datos()

    def validar_datos(self):
        """
        Valida que los datos del cliente sean correctos. 
        Si hay un error, lanza una excepción ValueError.
        """
        # Comprobamos que el nombre exista y no sea una cadena vacía
        # (strip() quita espacios en blanco al inicio/final antes de comparar)
        if not self.nombre or self.nombre.strip() == "":
            raise ClienteInvalidoError("Error: El nombre del cliente es obligatorio.")
            
        # Validación básica de correo:
        # - que no esté vacío
        # - que contenga el símbolo "@"
        # - que contenga al menos un punto "."
        # (es una validación simple, no cubre todos los formatos de correo inválidos)
        if not self.correo or "@" not in self.correo or "." not in self.correo:
            raise ClienteInvalidoError(f"Error: El correo '{self.correo}' no tiene un formato válido.")

    def describir(self) -> str:
        """
        Implementación del método abstracto 'describir' exigido por EntidadBase.
        """
        # Devuelve una cadena legible con los datos principales del cliente,
        # usando self.id (heredado de EntidadBase)
        return f"Cliente [ID: {self.id}] - Nombre: {self.nombre} - Correo: {self.correo}"
