
NOMBRE_EXCEL = "control_horarios_viajes.xlsx"

# Opciones de los Combobox
DEPARTAMENTOS = [
    "Reservas y Emisiones",
    "Atencion al Cliente",
    "Marketing y Ofertas",
    "Administración",
    "Gestión de Paquetes"
]

TIPOS_REGISTRO = [
    "Entrada a Turno",
    "Salida a Pausa",
    "Regreso de Pausa",
    "Salida de Turno"
]
#Acciones posibles según el estado actual del empleado y el tipo de registro
ACCIONES = {
    "Fuera de turno": {
        "Entrada a Turno": "Trabajando"
    },
    "Trabajando": {
        "Salida a Pausa": "Pausa",
        "Salida de Turno": "Fuera de turno"
    },
    "Pausa": {
        "Regreso de Pausa": "Trabajando"
    }
}

COLUMNAS_EXCEL = [
    "ID", "Nombre", "Departamento", "Acción", "Fecha", "Hora", "Observaciones"
]
