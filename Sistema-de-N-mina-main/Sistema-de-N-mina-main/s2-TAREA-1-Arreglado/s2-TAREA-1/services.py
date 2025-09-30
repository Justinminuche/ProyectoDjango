import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models import Empleado, Nomina, DetalleNomina, validate_empleado
from functools import reduce
import os
import datetime
import time

def clear_screen():
    """Limpia la pantalla del terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Repositorio(ABC):
    """Clase abstracta que define la interfaz para la persistencia de datos."""
    @abstractmethod
    def cargar_datos(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def guardar_datos(self, datos: List[Dict[str, Any]]):
        pass

class RepositorioEmpleados(Repositorio):
    """Implementación concreta del repositorio para los empleados, usando un archivo JSON."""
    def __init__(self, archivo: str = 'empleados.json'):
        self.archivo = archivo
        
    def cargar_datos(self) -> List[Dict[str, Any]]:
        """Lee los datos de empleados desde el archivo JSON."""
        if not os.path.exists(self.archivo):
            return []
        with open(self.archivo, 'r') as f:
            return json.load(f)

    def guardar_datos(self, datos: List[Dict[str, Any]]):
        """Guarda los datos de empleados en el archivo JSON."""
        with open(self.archivo, 'w') as f:
            json.dump(datos, f, indent=2)

class GestorEmpleados:
    """
    Clase que gestiona las operaciones de CRUD para los empleados.
    Interactúa con el Repositorio para la persistencia.
    """
    def __init__(self, repo: RepositorioEmpleados):
        self.repo = repo
        self.empleados: List[Empleado] = self.cargar_empleados()

    def cargar_empleados(self) -> List[Empleado]:
        """Carga los empleados desde el repositorio."""
        datos = self.repo.cargar_datos()
        return [Empleado(**e) for e in datos]

    def guardar_empleados(self):
        """Guarda la lista de empleados en el repositorio."""
        datos = [e.to_dict() for e in self.empleados]
        self.repo.guardar_datos(datos)

    @validate_empleado
    def crear_empleado(self, nuevo_empleado: Dict[str, Any]):
        """Crea un nuevo empleado si no existe y lo guarda."""
        if any(e.cedula == nuevo_empleado['cedula'] for e in self.empleados):
            print("Error: Ya existe un empleado con esa cédula.")
            return False
        self.empleados.append(Empleado(**nuevo_empleado))
        self.guardar_empleados()
        return True

    def consultar_empleados(self) -> List[Empleado]:
        """Devuelve la lista completa de empleados."""
        return self.empleados

    def modificar_empleado(self, cedula: str, cambios: Dict[str, Any]):
        """Modifica los datos de un empleado existente."""
        empleado_encontrado: Optional[Empleado] = next((e for e in self.empleados if e.cedula == cedula), None)
        if not empleado_encontrado:
            print("Error: Empleado no encontrado.")
            return False
        for key, value in cambios.items():
            setattr(empleado_encontrado, key, value)
        self.guardar_empleados()
        return True

    def eliminar_empleado(self, cedula: str):
        """Elimina un empleado de la lista y del archivo."""
        empleado_encontrado = next((e for e in self.empleados if e.cedula == cedula), None)
        if not empleado_encontrado:
            print("Error: Empleado no encontrado.")
            return False
        self.empleados.remove(empleado_encontrado)
        self.guardar_empleados()
        return True

class GestorNominas:
    """Clase que maneja la generación de nóminas y las consultas estadísticas."""
    def __init__(self, gestor_empleados: GestorEmpleados):
        self.gestor_empleados = gestor_empleados

    def generar_nomina_mensual(self):
        """Genera y guarda la nómina mensual para todos los empleados."""
        empleados = self.gestor_empleados.consultar_empleados()
        if not empleados:
            print("No hay empleados para generar la nómina.")
            return
        
        id_nomina = len(os.listdir('.')) + 1 # Generación simple de un ID
        aniomes = datetime.date.today().strftime('%Y%m')
        
        nomina = Nomina(id=id_nomina, aniomes=aniomes)
        
        id_detalle = 1
        for empleado in empleados:
            detalle = nomina.generar_detalle(empleado, id_detalle)
            nomina.agregar_detalle(detalle)
            id_detalle += 1
        
        nombre_archivo = f"nomina_{aniomes}.json"
        with open(nombre_archivo, 'w') as f:
            json.dump(nomina.to_dict(), f, indent=2)
            
        print(f"Nómina generada exitosamente en {nombre_archivo}")

    def consultar_estadisticas_nomina(self, aniomes: str):
        """Lee una nómina y muestra estadísticas detalladas."""
        nombre_archivo = f"nomina_{aniomes}.json"
        if not os.path.exists(nombre_archivo):
            print("Error: No se encontró la nómina para el mes y año especificados.")
            return

        with open(nombre_archivo, 'r') as f:
            datos_nomina = json.load(f)
        
        # Reconstruye el objeto Nomina para facilitar las consultas
        nomina = Nomina(id=datos_nomina['id'], aniomes=datos_nomina['aniomes'])
        nomina.detalles = [DetalleNomina(
            id=d['id'],
            # Se crea un objeto Empleado "dummy" solo con los datos necesarios para las consultas
            empleado=Empleado(cedula="", nombre=d['empleado'], sueldo=d['sueldo'], departamento="", cargo=""),
            sueldo=d['sueldo'],
            bono=d['bono'],
            prestamo=d['prestamo']
        ) for d in datos_nomina['detalles']]

        print(f"\n--- Estadísticas de Nómina {aniomes} ---")
        
        # Consultas usando funciones de orden superior y list comprehensions
        total_empleados = len(nomina.detalles)
        total_neto = reduce(lambda acumulado, detalle: acumulado + detalle.neto, nomina.detalles, 0.0)
        
        sueldos = [d.sueldo for d in nomina.detalles]
        promedio_sueldos = sum(sueldos) / len(sueldos) if sueldos else 0
        
        empleados_alto_sueldo = list(filter(lambda d: d.sueldo > 1000, nomina.detalles))
        nombres_altos = [d.empleado.nombre for d in empleados_alto_sueldo]
        
        mayor_neto = max(nomina.detalles, key=lambda d: d.neto, default=None)
        menor_neto = min(nomina.detalles, key=lambda d: d.neto, default=None)

        print(f"Total de empleados en nómina: {total_empleados}")
        print(f"Total neto pagado: ${total_neto:,.2f}")
        print(f"Promedio de sueldos: ${promedio_sueldos:,.2f}")
        print(f"Empleados con sueldo > $1000: {nombres_altos}")
        
        if mayor_neto:
            print(f"Empleado con mayor neto: {mayor_neto.empleado.nombre} (${mayor_neto.neto:,.2f})")
            
        if menor_neto:
            print(f"Empleado con menor neto: {menor_neto.empleado.nombre} (${menor_neto.neto:,.2f})")