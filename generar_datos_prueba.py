"""Añade fichajes de ejemplo de los últimos 30 días sin duplicarlos."""

from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

from openpyxl import load_workbook

from excel_manager import ExcelManager


ARCHIVO = Path(__file__).resolve().parent / "data" / "control_horarios_viajes.xlsx"
MARCA = "Datos de prueba del panel"
EMPLEADOS = (
    ("DEMO001", "Lucía Martín", "Reservas y Emisión"),
    ("DEMO002", "Diego Ruiz", "Atención al Cliente"),
    ("DEMO003", "Marta Sánchez", "Operaciones"),
    ("DEMO004", "Pablo Torres", "Recursos Humanos"),
    ("DEMO005", "Elena López", "Administración"),
    ("DEMO006", "Sofía Romero", "Reservas y Emisión"),
    ("DEMO007", "Javier Díaz", "Atención al Cliente"),
    ("DEMO008", "Carmen Vega", "Operaciones"),
    ("DEMO009", "Andrés Pérez", "Administración"),
    ("DEMO010", "Nuria Castro", "Recursos Humanos"),
)


def generar():
    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    ExcelManager(ARCHIVO)
    libro = load_workbook(ARCHIVO)
    try:
        hoja = libro["Registros"]
        encabezados = [celda.value for celda in hoja[1]]
        columnas = {nombre: indice for indice, nombre in enumerate(encabezados)}
        registros = list(hoja.iter_rows(min_row=2, values_only=True))
        existentes = {
            (fila[columnas["id_empleado"]], fila[columnas["fecha"]],
             fila[columnas["accion"]]): indice
            for indice, fila in enumerate(registros, start=2)
            if str(fila[columnas["observaciones"]] or "").startswith(MARCA)
        }
        ids = [fila[columnas["id_registro"]] for fila in registros]
        siguiente_id = max((valor for valor in ids if type(valor) is int), default=0) + 1
        ahora = datetime.now()
        hoy = ahora.date()
        aleatorio = Random(20261028)
        nuevos = 0
        corregidos = 0

        for dias_atras in range(30, -1, -1):
            dia = hoy - timedelta(days=dias_atras)
            cantidad = 3 if dia.weekday() >= 5 else 6 + aleatorio.randrange(4)
            empleados = aleatorio.sample(EMPLEADOS, cantidad)
            if dia == hoy:
                empleados = list(EMPLEADOS[:8])

            for indice, (identificador, nombre, departamento) in enumerate(empleados):
                hora_entrada = datetime.combine(dia, datetime.min.time()).replace(
                    hour=8 + aleatorio.randrange(2), minute=aleatorio.randrange(0, 60, 10)
                )
                hora_salida = hora_entrada + timedelta(
                    hours=7 + aleatorio.randrange(2), minutes=aleatorio.randrange(0, 60, 15)
                )
                acciones = [("Entrada a Turno", hora_entrada)]
                if dia != hoy or indice < 6:
                    acciones.append(("Salida de Turno", hora_salida))
                if dia == hoy:
                    entrada_hoy = max(
                        datetime.combine(hoy, datetime.min.time()),
                        ahora - timedelta(minutes=110 + indice * 5),
                    )
                    salida_hoy = max(
                        entrada_hoy, ahora - timedelta(minutes=5 + indice)
                    )
                    acciones = [("Entrada a Turno", entrada_hoy)]
                    if indice < 6:
                        acciones.append(("Salida de Turno", salida_hoy))

                for accion, momento in acciones:
                    clave = (identificador, dia.isoformat(), accion)
                    if clave in existentes:
                        fila = existentes[clave]
                        hora_guardada = str(hoja.cell(fila, columnas["hora"] + 1).value)
                        if dia == hoy and hora_guardada > ahora.strftime("%H:%M:%S"):
                            hoja.cell(fila, columnas["hora"] + 1).value = momento.strftime("%H:%M:%S")
                            corregidos += 1
                        continue
                    registro = {
                        "id_registro": siguiente_id,
                        "id_empleado": identificador,
                        "nombre_completo": nombre,
                        "departamento": departamento,
                        "accion": accion,
                        "fecha": dia.isoformat(),
                        "hora": momento.strftime("%H:%M:%S"),
                        "observaciones": MARCA,
                        "hora_inicio_prevista": "09:00",
                        "hora_fin_prevista": "17:00",
                    }
                    hoja.append([registro.get(nombre) for nombre in encabezados])
                    existentes[clave] = hoja.max_row
                    siguiente_id += 1
                    nuevos += 1

        if nuevos or corregidos:
            libro.save(ARCHIVO)
        return nuevos
    finally:
        libro.close()


if __name__ == "__main__":
    print(f"Fichajes de prueba añadidos: {generar()}")
