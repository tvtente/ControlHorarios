"""Permite registrar y consultar fichajes desde la consola."""

from pathlib import Path
from excel_manager import ExcelManager

def main():
    carpeta_datos = Path(__file__).resolve().parent / "data"
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    excel = ExcelManager(carpeta_datos / "control_horarios.xlsx")

    print("1. Register a record")
    print("2. Show all records")

    option = input("Choose an option: ").strip()

    if option == "1":
        try:
            record = excel.guardar_registro(
                id_empleado=input("Employee ID: "),
                nombre_completo=input("Full name: "),
                departamento=input("Department: "),
                accion=input("Action: "),
                observaciones=input("Observations (optional): "),
            )
            print("\nRecord saved successfully:")
            print(record)

        except ValueError as error:
            print("Validation error:", error)

    elif option == "2":
        records = excel.consultar_registros()

        if not records:
            print("No records found.")
        else:
            for record in records:
                print(record)

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
