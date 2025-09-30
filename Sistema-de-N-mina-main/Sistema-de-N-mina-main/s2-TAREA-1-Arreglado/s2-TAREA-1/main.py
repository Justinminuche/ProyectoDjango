# main.py
import os
import time
import re  # Para validaciones con expresiones regulares
from services import GestorEmpleados, RepositorioEmpleados, GestorNominas, clear_screen

def menu_principal():
    """Muestra el menú principal y solicita una opción válida."""
    while True:
        print("\n--- Sistema de Gestión de Nóminas ---")
        print("1. Gestión de Empleados (CRUD)")
        print("2. Generar Nómina Mensual")
        print("3. Consultar Estadísticas de Nómina")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion in ['1', '2', '3', '4']:
            return opcion
        else:
            print("⚠️ Opción inválida. Intente de nuevo.\n")

def menu_empleados():
    """Muestra el menú de gestión de empleados y valida la opción."""
    while True:
        print("\n--- Gestión de Empleados ---")
        print("1. Crear nuevo empleado")
        print("2. Consultar todos los empleados")
        print("3. Modificar empleado")
        print("4. Eliminar empleado")
        print("5. Volver al menú principal")
        opcion = input("Seleccione una opción: ")
        if opcion in ['1', '2', '3', '4', '5']:
            return opcion
        else:
            print("⚠️ Opción inválida. Intente de nuevo.\n")

def validar_cedula():
    """Solicita y valida una cédula de 10 dígitos."""
    while True:
        cedula = input("Cédula (10 dígitos): ")
        if cedula.isdigit() and len(cedula) == 10:
            return cedula
        print("⚠️ La cédula debe contener exactamente 10 dígitos.")
        time.sleep(2)
        clear_screen()

def validar_texto(campo):
    """Solicita un campo que solo contenga letras y espacios."""
    while True:
        valor = input(f"{campo} (solo texto): ")
        if valor.replace(" ", "").isalpha():
            return valor
        print(f"⚠️ El {campo} solo puede contener letras.")
        time.sleep(2)
        clear_screen()

def validar_sueldo(mensaje="Sueldo: "):
    """Solicita y valida que el sueldo sea un número positivo."""
    while True:
        sueldo_input = input(mensaje)
        if sueldo_input.replace('.', '', 1).isdigit():
            sueldo = float(sueldo_input)
            if sueldo > 0:
                return sueldo
            print("⚠️ El sueldo debe ser un número positivo.")
        else:
            print("⚠️ El sueldo solo puede contener números.")
        time.sleep(2)
        clear_screen()

def main():
    """Función principal que ejecuta el programa."""
    repo_empleados = RepositorioEmpleados()
    gestor_empleados = GestorEmpleados(repo_empleados)
    gestor_nominas = GestorNominas(gestor_empleados)

    while True:
        opcion = menu_principal()
        time.sleep(1)
        clear_screen()

        if opcion == '1':  # Gestión de empleados
            while True:
                opcion_empleado = menu_empleados()
                time.sleep(1)
                clear_screen()

                if opcion_empleado == '1':  # Crear
                    cedula = validar_cedula()
                    nombre = validar_texto("Nombre")
                    sueldo = validar_sueldo()
                    departamento = validar_texto("Departamento")
                    cargo = validar_texto("Cargo")

                    if gestor_empleados.crear_empleado({
                        'cedula': cedula,
                        'nombre': nombre,
                        'sueldo': sueldo,
                        'departamento': departamento,
                        'cargo': cargo
                    }):
                        print("✅ Empleado creado exitosamente.")
                    time.sleep(2)

                elif opcion_empleado == '2':  # Consultar
                    empleados = gestor_empleados.consultar_empleados()
                    if empleados:
                        print("\n--- Lista de Empleados ---")
                        for emp in empleados:
                            print(f"Cédula: {emp.cedula}, Nombre: {emp.nombre}, "
                                  f"Sueldo: ${emp.sueldo:,.2f}, Departamento: {emp.departamento}, Cargo: {emp.cargo}")
                    else:
                        print("⚠️ No hay empleados registrados.")
                    time.sleep(3)

                elif opcion_empleado == '3':  # Modificar
                    cedula = validar_cedula()
                    cambios = {}
                    nombre = input("Nuevo nombre (deje en blanco si no cambia): ")
                    if nombre:
                        if nombre.replace(" ", "").isalpha():
                            cambios['nombre'] = nombre
                        else:
                            print("⚠️ El nombre solo puede contener letras.")

                    sueldo_input = input("Nuevo sueldo (deje en blanco si no cambia): ")
                    if sueldo_input:
                        if sueldo_input.replace('.', '', 1).isdigit():
                            sueldo = float(sueldo_input)
                            if sueldo > 0:
                                cambios['sueldo'] = sueldo
                            else:
                                print("⚠️ El sueldo debe ser positivo.")
                        else:
                            print("⚠️ El sueldo solo puede contener números.")

                    departamento = input("Nuevo departamento (deje en blanco si no cambia): ")
                    if departamento:
                        if departamento.replace(" ", "").isalpha():
                            cambios['departamento'] = departamento
                        else:
                            print("⚠️ El departamento solo puede contener letras.")

                    cargo = input("Nuevo cargo (deje en blanco si no cambia): ")
                    if cargo:
                        if cargo.replace(" ", "").isalpha():
                            cambios['cargo'] = cargo
                        else:
                            print("⚠️ El cargo solo puede contener letras.")

                    if cambios and gestor_empleados.modificar_empleado(cedula, cambios):
                        print("✅ Empleado modificado exitosamente.")
                    time.sleep(3)

                elif opcion_empleado == '4':  # Eliminar
                    cedula = validar_cedula()
                    confirm = input(f"¿Está seguro de eliminar al empleado con cédula {cedula}? (s/n): ")
                    if confirm.lower() == 's':
                        if gestor_empleados.eliminar_empleado(cedula):
                            print("✅ Empleado eliminado exitosamente.")
                    time.sleep(2)

                elif opcion_empleado == '5':
                    break

                time.sleep(2)
                clear_screen()

        elif opcion == '2':  # Generar nómina
            gestor_nominas.generar_nomina_mensual()
            time.sleep(3)
            clear_screen()

        elif opcion == '3':  # Consultar estadísticas
            while True:
                aniomes = input("Ingrese el año y mes de la nómina (YYYYMM, ej. 202401): ")
                if re.fullmatch(r'^\d{6}$', aniomes):
                    gestor_nominas.consultar_estadisticas_nomina(aniomes)
                    break
                else:
                    print("⚠️ Formato inválido. Debe ser YYYYMM (ej: 202401).")
            time.sleep(3)
            clear_screen()

        elif opcion == '4':  # Salir
            print("👋 Saliendo del sistema...")
            time.sleep(1)
            clear_screen()
            break

if __name__ == "__main__":
    main()
