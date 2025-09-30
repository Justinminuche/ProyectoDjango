import json
from typing import List, Dict, Any, Callable
from functools import wraps
import re

def validate_empleado(func: Callable) -> Callable:
    """
    Decorador para validar los datos de un empleado antes de la creación o actualización.
    Verifica que el sueldo sea positivo, que la cédula cumpla con el formato y
    que los campos de texto solo contengan letras y espacios.
    """
    @wraps(func)
    def wrapper(self, empleado: Dict[str, Any]):
        # Valida que la entrada sea un diccionario y contenga todos los campos.
        if not isinstance(empleado, dict):
            raise TypeError("El empleado debe ser un diccionario.")
        if not all(k in empleado for k in ['cedula', 'nombre', 'sueldo', 'departamento', 'cargo']):
            raise ValueError("Faltan campos requeridos para el empleado.")

        # Validaciones de tipo de dato y formato.
        if not isinstance(empleado['sueldo'], (int, float)) or empleado['sueldo'] <= 0:
            raise ValueError("El sueldo debe ser un número positivo.")
        
        # Validación de la cédula: 10 dígitos numéricos.
        cedula_str = str(empleado['cedula'])
        if not cedula_str.isdigit() or len(cedula_str) != 10:
            raise ValueError("La cédula debe ser un número de 10 dígitos exactamente.")
        
        # Validación de campos de texto con expresiones regulares.
        # Permite letras y espacios, pero no números ni símbolos.
        if not re.fullmatch(r'^[a-zA-Z\s]+$', empleado['nombre']):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        
        if not re.fullmatch(r'^[a-zA-Z\s]+$', empleado['departamento']):
            raise ValueError("El departamento solo puede contener letras y espacios.")
        
        if not re.fullmatch(r'^[a-zA-Z\s]+$', empleado['cargo']):
            raise ValueError("El cargo solo puede contener letras y espacios.")
            
        return func(self, empleado)
    return wrapper

class Empleado:
    """Clase que representa a un empleado de la empresa."""
    def __init__(self, cedula: str, nombre: str, sueldo: float, departamento: str, cargo: str):
        self.cedula = cedula
        self.nombre = nombre
        self.sueldo = sueldo
        self.departamento = departamento
        self.cargo = cargo

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Empleado en un diccionario para guardarlo en JSON."""
        return self.__dict__

class DetalleNomina:
    """Clase que representa el cálculo de la nómina para un empleado en particular."""
    def __init__(self, id: int, empleado: Empleado, sueldo: float, bono: float, prestamo: float):
        self.id = id
        self.empleado = empleado
        self.sueldo = sueldo
        self.bono = bono
        
        # Cálculos de ingresos y descuentos.
        self.tot_ing = self.sueldo + self.bono
        self.iess = round(self.sueldo * 0.0945, 2)
        self.prestamo = prestamo
        self.tot_des = self.iess + self.prestamo
        self.neto = self.tot_ing - self.tot_des

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto DetalleNomina en un diccionario para JSON."""
        return {
            "id": self.id,
            "empleado": self.empleado.nombre,
            "sueldo": self.sueldo,
            "bono": self.bono,
            "tot_ing": self.tot_ing,
            "iess": self.iess,
            "prestamo": self.prestamo,
            "tot_des": self.tot_des,
            "neto": self.neto
        }

class Nomina:
    """Clase principal que representa la nómina mensual consolidada."""
    BONO = 50.0  # Atributo de clase para el valor del bono.
    PRESTAMO = 20.0 # Atributo de clase para el valor del préstamo.

    def __init__(self, id: int, aniomes: str):
        self.id = id
        self.aniomes = aniomes
        self.tot_ing = 0.0
        self.tot_des = 0.0
        self.neto = 0.0
        self.detalles: List[DetalleNomina] = []

    def generar_detalle(self, empleado: Empleado, id_detalle: int) -> DetalleNomina:
        """
        Función interna para crear un DetalleNomina. Encapsula la lógica de
        cálculo para un solo empleado.
        """
        return DetalleNomina(
            id=id_detalle,
            empleado=empleado,
            sueldo=empleado.sueldo,
            bono=self.BONO,
            prestamo=self.PRESTAMO
        )
    
    def agregar_detalle(self, detalle: DetalleNomina):
        """Agrega un detalle de nómina y actualiza los totales."""
        self.detalles.append(detalle)
        self.tot_ing += detalle.tot_ing
        self.tot_des += detalle.tot_des
        self.neto += detalle.neto

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Nomina en un diccionario para JSON."""
        return {
            "id": self.id,
            "aniomes": self.aniomes,
            "tot_ing": self.tot_ing,
            "tot_des": self.tot_des,
            "neto": self.neto,
            "detalles": [d.to_dict() for d in self.detalles]
        }