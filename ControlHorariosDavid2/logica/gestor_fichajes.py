import datetime
from config import ACCIONES

class GestorFichajes:
    def __init__(self, gestor_excel):
        self.gestor_excel = gestor_excel
        self.estado_actual = "Fuera de turno"
        
    def validacion_campos(self, id, nombre, departamento, accion):
        if not id:
            return "El campo ID es obligatorio"
        if not nombre:
            return "El campo Nombre es obligatorio"
        if not departamento:
            return "El campo Departamento es obligatorio"
        if not accion:
            return "El campo Acción es obligatorio"
        return None
    
    def validar_id_empleado(self, id, nombre, registros):
        
        for registro in registros:
            if str(registro[0]).strip() == str(id).strip() and registro[1].strip().casefold() != nombre.casefold().strip().casefold():
                return f"El ID {id} ya está asociado al nombre {registro[1]}"
            continue
    
    def obtener_estado_actual(self, id, registros):
        estado = self.estado_actual
        for registro in registros:
            if str(registro[0]).strip() == str(id).strip():
                accion = registro[3]
                if  estado in ACCIONES and accion in ACCIONES[estado]:
                    estado = ACCIONES[estado][accion]
        return estado
    
    def validar_accion(self,id,  accion, registros):
        estado = self.obtener_estado_actual(id, registros)
        if estado in ACCIONES and accion not in ACCIONES[estado]:
            raise ValueError(f"La acción '{accion}' no es válida desde el estado '{estado}'")
        return None
    
    def calcular_empleados_hoy(self, registros):
        fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
        empleados_hoy = set()
        for registro in registros:
            if registro[4] == fecha_actual and registro[0] is not None:
                empleados_hoy.add(registro[0])
        print(f"Empleados hoy: {empleados_hoy}")
        return len(empleados_hoy)
    
    def calcular_departamentos(self, registros):
        fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
        departamentos_hoy = []
        for registro in registros:
            if registro[4] == fecha_actual and registro[2] is not None:
                departamentos_hoy.append(registro[2])
        print(f"Departamentos hoy: {departamentos_hoy}")
        return len(departamentos_hoy)
    
    def registrar_fichaje(self, id, nombre, departamento, accion, observaciones):
        print(f"Registrando fichaje: ID={id}, Nombre={nombre}, Departamento={departamento}, Acción={accion}, Observaciones={observaciones}")
        registros = self.gestor_excel.obtener_registros_excel()
        validacion = self.validacion_campos(id, nombre, departamento, accion)
        if validacion:
            raise ValueError(validacion)
        validacion_id = self.validar_id_empleado(id, nombre, registros)
        if validacion_id:
            raise ValueError(validacion_id)
        
        validacion_accion = self.validar_accion(id, accion, registros)
        if validacion_accion:
            raise ValueError(validacion_accion)
        fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        nuevo_registro = [id, nombre, departamento, accion, fecha_actual, hora_actual, observaciones]
        print(f"Nuevo registro: {nuevo_registro}")
        self.gestor_excel.guardar_excel(nuevo_registro)
        
        return True