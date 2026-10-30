"""Reglas de negocio independientes de Tkinter y de openpyxl."""

from datetime import date, datetime


class ServicioFichajes:
    ACCIONES = {
        "Fuera de turno": {"Entrada a Turno": "Trabajando"},
        "Trabajando": {"Salida a Pausa": "Pausa", "Salida de Turno": "Fuera de turno"},
        "Pausa": {"Regreso de Pausa": "Trabajando"},
    }

    @staticmethod
    def _es_hoy(valor, hoy):
        if isinstance(valor, datetime):
            return valor.date() == hoy
        if isinstance(valor, date):
            return valor == hoy
        try:
            return datetime.strptime(str(valor), "%d-%m-%Y").date() == hoy
        except ValueError:
            return False

    def obtener_estado_empleado(self, id_empleado, registros, hoy=None):
        """Calcula el estado solo con los movimientos de la jornada actual."""
        hoy = hoy or date.today()
        estado = "Fuera de turno"
        for registro in registros:
            if (str(registro[0] or "").strip() == id_empleado.strip()
                    and self._es_hoy(registro[4], hoy)):
                accion = registro[3]
                estado = self.ACCIONES.get(estado, {}).get(accion, estado)
        return estado

    def validacion_campos(self, id_empleado, nombre, departamento, tipo_accion,
                          registros, hoy=None):
        """Valida campos, identidad y la acción permitida."""
        for valor, etiqueta in (
            (id_empleado, "ID"), (nombre, "Nombre"),
            (departamento, "Departamento"), (tipo_accion, "Tipo de Registro"),
        ):
            if not valor.strip():
                raise ValueError(f"El campo {etiqueta} es obligatorio.")
        self.validar_id_empleado(id_empleado, nombre, departamento, registros)
        self.validar_accion(id_empleado, tipo_accion, registros, hoy)

    def validar_id_empleado(self, id_empleado, nombre, departamento, registros):
        """Evita que un ID ya registrado cambie de nombre o departamento."""
        for registro in registros:
            if str(registro[0] or "").strip() != id_empleado.strip():
                continue
            if str(registro[1] or "").strip().casefold() != nombre.strip().casefold():
                raise ValueError(f"El ID '{id_empleado}' ya está asociado a otro nombre.")
            if str(registro[2] or "").strip() != departamento.strip():
                raise ValueError(f"El ID '{id_empleado}' ya está asociado a otro departamento.")

    def validar_accion(self, id_empleado, accion, registros, hoy=None):
        """Comprueba que el movimiento corresponda al estado de hoy."""
        estado = self.obtener_estado_empleado(id_empleado, registros, hoy)
        if accion not in self.ACCIONES[estado]:
            raise ValueError(f"La acción '{accion}' no es válida para el estado actual '{estado}'.")

    def crear_registro(self, id_empleado, nombre, departamento, accion,
                       observaciones, registros, ahora=None):
        ahora = ahora or datetime.now()
        self.validacion_campos(id_empleado, nombre, departamento, accion,
                               registros, ahora.date())
        return [id_empleado.strip(), nombre.strip(), departamento.strip(), accion.strip(),
                ahora.strftime("%d-%m-%Y"), ahora.strftime("%H:%M:%S"),
                observaciones.strip()]

    def calcular_registros_hoy(self, registros, hoy=None):
        hoy = hoy or date.today()
        return len({registro[0] for registro in registros
                    if registro[0] is not None and self._es_hoy(registro[4], hoy)})

    def calcular_departamentos(self, registros, hoy=None):
        hoy = hoy or date.today()
        return len({registro[2] for registro in registros
                    if registro[2] and self._es_hoy(registro[4], hoy)})
