"""Permite registrar y consultar fichajes desde la consola."""
from pathlib import Path
from excel_manager import ExcelManager


def mostrar_registro(registro):
    print(f"{registro.get('fecha', '')} {registro.get('hora', '')} | "
          f"{registro.get('id_empleado', '')} | {registro.get('nombre_completo', '')} | "
          f"{registro.get('departamento', '')} | {registro.get('accion', '')}")


def main():
    carpeta_datos = Path(__file__).resolve().parent / 'data'
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    try:
        excel = ExcelManager(carpeta_datos / 'control_horarios.xlsx')
        print('1. Registrar un fichaje')
        print('2. Consultar todos los fichajes')
        opcion = input('Elige una opción: ').strip()
        if opcion == '1':
            identificador = input('ID del empleado (EMP-000): ')
            nombre = input('Nombre completo: ')
            print('Departamentos disponibles: ' + ', '.join(excel.consultar_departamentos()))
            departamento = input('Departamento: ')
            acciones = ('Entrada a Turno', 'Salida de Turno', 'Inicio de Descanso', 'Fin de Descanso')
            for numero, accion in enumerate(acciones, 1):
                print(f'{numero}. {accion}')
            seleccion = input('Tipo de registro (1–4): ').strip()
            if seleccion not in ('1', '2', '3', '4'):
                raise ValueError('Selecciona un tipo de registro entre 1 y 4.')
            horario = excel.consultar_horario_departamento(departamento)
            registro = excel.guardar_registro(
                id_empleado=identificador, nombre_completo=nombre,
                departamento=departamento, accion=acciones[int(seleccion)-1],
                observaciones=input('Observaciones (opcional): '), **horario,
            )
            print('\nFichaje guardado correctamente:')
            mostrar_registro(registro)
        elif opcion == '2':
            registros = excel.consultar_registros()
            if not registros:
                print('No se encontraron fichajes.')
            for registro in registros:
                mostrar_registro(registro)
        else:
            print('Opción no válida. Elige 1 o 2.')
    except ValueError as error:
        print('Revisa los datos:', error)
    except PermissionError:
        print('No se puede acceder al Excel. Ciérralo si está abierto y comprueba los permisos del archivo.')
    except OSError:
        print('No se ha podido acceder al archivo de fichajes. Comprueba su ubicación y los permisos.')


if __name__ == '__main__':
    main()
