from pathlib import Path
from datetime import datetime
from openpyxl import Workbook, load_workbook


class ExcelManager:

    HEADERS = [
        "id_registro",
        "id_empleado",
        "nombre_completo",
        "departamento",
        "accion",
        "fecha",
        "hora",
        "observaciones",
        "hora_inicio_prevista",
        "hora_fin_prevista"
    ]

    def __init__(self, filename="control_horarios_viajes.xlsx"):
        self.filename = Path(filename)
        self.inicializar_excel()

    # Create the workbook if needed and preserve existing records
    def inicializar_excel(self):
        if not self.filename.exists():
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Registros"
            sheet.append(self.HEADERS)
            workbook.save(self.filename)
            workbook.close()
            return

        workbook = load_workbook(self.filename)

        try:
            if "Registros" not in workbook.sheetnames:
                raise ValueError("The Excel file has no 'Registros' sheet.")

            sheet = workbook["Registros"]

            existing_headers = [
                sheet.cell(row=1, column=col).value
                for col in range(1, sheet.max_column + 1)
            ]

            # Add missing columns without deleting existing records
            if not existing_headers or all(h is None for h in existing_headers):
                sheet.append(self.HEADERS)
            else:
                for header in self.HEADERS:
                    if header not in existing_headers:
                        existing_headers.append(header)
                        sheet.cell(
                            row=1, column=len(existing_headers)
                        ).value = header

            workbook.save(self.filename)
        finally:
            workbook.close()

    # Validate required fields and append a new record
    def guardar_registro(
        self,
        id_empleado,
        nombre_completo,
        departamento,
        accion,
        observaciones="",
        hora_inicio_prevista="",
        hora_fin_prevista=""
    ):
        if not isinstance(id_empleado, str) or not id_empleado.strip():
            raise ValueError("Employee ID is required.")

        if not isinstance(nombre_completo, str) or not nombre_completo.strip():
            raise ValueError("Full name is required.")

        if not isinstance(departamento, str) or not departamento.strip():
            raise ValueError("Department is required.")

        if not isinstance(accion, str) or not accion.strip():
            raise ValueError("Action is required.")

        if not isinstance(observaciones, str):
            raise ValueError("Observations must be text.")

        if not isinstance(hora_inicio_prevista, str):
            raise ValueError("Planned start time must be text.")

        if not isinstance(hora_fin_prevista, str):
            raise ValueError("Planned end time must be text.")

        # Generate an ID and capture the current date and time
        registros = self.consultar_registros()
        ids = [
            r["id_registro"]
            for r in registros
            if isinstance(r.get("id_registro"), int)
            and not isinstance(r.get("id_registro"), bool)
        ]
        nuevo_id = max(ids, default=0) + 1
        ahora = datetime.now()

        registro = {
            "id_registro": nuevo_id,
            "id_empleado": id_empleado.strip(),
            "nombre_completo": nombre_completo.strip(),
            "departamento": departamento.strip(),
            "accion": accion.strip(),
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "observaciones": observaciones.strip(),
            "hora_inicio_prevista": hora_inicio_prevista.strip(),
            "hora_fin_prevista": hora_fin_prevista.strip()
        }

        workbook = load_workbook(self.filename)

        try:
            sheet = workbook["Registros"]
            headers = [
                sheet.cell(row=1, column=col).value
                for col in range(1, sheet.max_column + 1)
            ]
            sheet.append([registro.get(header) for header in headers])
            workbook.save(self.filename)
        finally:
            workbook.close()

        return registro

    # Return all records, optionally filtered by employee, department, or action
    def consultar_registros(
        self, empleado="", departamento="", accion=""
    ):
        workbook = load_workbook(self.filename, read_only=True)

        try:
            sheet = workbook["Registros"]
            rows = sheet.iter_rows(values_only=True)
            headers = next(rows, None)

            if not headers:
                return []

            registros = [
                dict(zip(headers, row))
                for row in rows
                if any(value is not None for value in row)
            ]

            if empleado.strip():
                termino = empleado.strip().lower()
                registros = [
                    r for r in registros
                    if termino in str(r.get("id_empleado") or "").lower()
                    or termino in str(r.get("nombre_completo") or "").lower()
                ]

            if departamento.strip():
                termino = departamento.strip().lower()
                registros = [
                    r for r in registros
                    if termino in str(r.get("departamento") or "").lower()
                ]

            if accion.strip():
                termino = accion.strip().lower()
                registros = [
                    r for r in registros
                    if termino in str(r.get("accion") or "").lower()
                ]

            return registros

        finally:
            workbook.close()

    def consultar_departamentos(self):
        """Devuelve los departamentos de la hoja Departamentos de Excel."""
        workbook = load_workbook(self.filename, read_only=True)

        try:
            if "Departamentos" not in workbook.sheetnames:
                return []

            sheet = workbook["Departamentos"]
            rows = sheet.iter_rows(values_only=True)
            headers = next(rows, None)

            if not headers:
                return []

            columna = next(
                (
                    indice
                    for indice, encabezado in enumerate(headers)
                    if str(encabezado or "").strip().lower() == "departamento"
                ),
                None,
            )

            if columna is None:
                return []

            departamentos = []

            for fila in rows:
                if columna < len(fila):
                    valor = fila[columna]

                    if valor is not None and str(valor).strip():
                        departamentos.append(str(valor).strip())

            return list(dict.fromkeys(departamentos))

        finally:
            workbook.close()