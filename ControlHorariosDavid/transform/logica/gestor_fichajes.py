"""Validaciones y estadísticas de fichajes independientes de Excel y Tkinter."""

import datetime

from config import ACCIONES


class GestorFichajes:
    def __init__(self, gestor_excel):
        self.gestor_excel = gestor_excel

    @staticmethod
    def _fecha_registro(valor):
        if isinstance(valor, datetime.datetime):
            return valor.date()
        if isinstance(valor, datetime.date):
            return valor
        try:
            return datetime.datetime.strptime(str(valor), "%d-%m-%Y").date()
        except ValueError:
            return None

    def validacion_campos(self, id, nombre, departamento, accion):
        for valor, campo in ((id, "ID"), (nombre, "Nombre"),
                             (departamento, "Departamento"), (accion, "Acción")):
            if not str(valor or "").strip():
                return f"El campo {campo} es obligatorio"
        return None

    def validar_id_empleado(self, id, nombre, departamento, registros):
        for registro in registros:
            if str(registro[0] or "").strip() != str(id).strip():
                continue
            if str(registro[1] or "").strip().casefold() != nombre.strip().casefold():
                return f"El ID {id} ya está asociado al nombre {registro[1]}"
            if str(registro[2] or "").strip() != departamento.strip():
                return f"El ID {id} ya está asociado al departamento {registro[2]}"
        return None

    def obtener_estado_actual(self, id, registros, hoy=None):
        """La jornada empieza de nuevo cada día."""
        hoy = hoy or datetime.date.today()
        estado = "Fuera de turno"
        for registro in registros:
            if (str(registro[0] or "").strip() == str(id).strip()
                    and self._fecha_registro(registro[4]) == hoy):
                accion = registro[3]
                estado = ACCIONES.get(estado, {}).get(accion, estado)
        return estado

    def validar_accion(self, id, accion, registros, hoy=None):
        estado = self.obtener_estado_actual(id, registros, hoy)
        if accion not in ACCIONES.get(estado, {}):
            return f"La acción '{accion}' no es válida desde el estado '{estado}'"
        return None

    def guardar_fichaje_excel(self, id, nombre, departamento, accion, observaciones,
                              ahora=None):
        """Valida y persiste un fichaje; devuelve la fila guardada."""
        ahora = ahora or datetime.datetime.now()
        error = self.validacion_campos(id, nombre, departamento, accion)
        if error:
            raise ValueError(error)
        registros = self.gestor_excel.obtener_registros_excel()
        error = (self.validar_id_empleado(id, nombre, departamento, registros)
                 or self.validar_accion(id, accion, registros, ahora.date()))
        if error:
            raise ValueError(error)
        registro = [id.strip(), nombre.strip(), departamento.strip(), accion,
                    ahora.strftime("%d-%m-%Y"), ahora.strftime("%H:%M:%S"),
                    observaciones.strip()]
        self.gestor_excel.guardar_excel(registro)
        return registro

    def calcular_empleados_hoy(self, registros, hoy=None):
        hoy = hoy or datetime.date.today()
        return len({registro[0] for registro in registros
                    if registro[0] and self._fecha_registro(registro[4]) == hoy})

    def calcular_departamentos(self, registros, hoy=None):
        hoy = hoy or datetime.date.today()
        return len({registro[2] for registro in registros
                    if registro[2] and self._fecha_registro(registro[4]) == hoy})
