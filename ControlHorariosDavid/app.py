import ttkbootstrap as ttkb
import tkinter as tk
import openpyxl as pxl
import datetime
from tkinter import messagebox
from pathlib import Path

RUTA = Path(__file__).resolve().parent
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

def inicializar_excel():
    
    if not Path(RUTA / NOMBRE_EXCEL).exists():
        libro = pxl.Workbook()
        hoja = libro.active
        hoja.append(["ID", "Nombre", "Departamento", "Acción","Fecha","Hora", "Observaciones"])
        libro.save(Path(RUTA / NOMBRE_EXCEL))
        return libro, hoja
    
    libro = pxl.load_workbook(Path(RUTA / NOMBRE_EXCEL))
    hoja = libro.active
    return libro, hoja
    

def obtener_datos_formulario():
    """Obtiene los datos ingresados en el formulario y los devuelve"""
    id_empleado = entry_id_empleado.get().strip()
    nombre_empleado = entry_nombre_empleado.get().strip()
    departamento = entry_departamento.get().strip()
    tipo_registro = entry_tipo_registro.get().strip()
    observaciones = entry_observaciones.get().strip()
    return id_empleado, nombre_empleado, departamento, tipo_registro, observaciones


def guardar_fichaje_excel():
    """Guarda el fichaje en el archivo Excel. 
    Obtiene los datos del formulario, valida los campos obligatorios,
    agrega un nuevo registro con la fecha y hora actuales, y actualiza el panel de control."""
    
    # Obtenemos los datos del formulario
    id, nombre, departamento, tipo, observaciones = obtener_datos_formulario()
    print(f"ID: {id}, Nombre: {nombre}, Departamento: {departamento}, Tipo: {tipo}, Observaciones: {observaciones}")

    # VALIDACIONES
    if not validacion_campos(id, nombre, departamento, tipo):
        return
    
    # Obtenemos la fecha y hora actuales
    fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Creamos un nuevo registro con los datos obtenidos y la fecha y hora actuales
    nuevo_registro = [id, nombre, departamento, tipo, fecha_actual, hora_actual, observaciones]
    
    #Guardamos el nuevo registro en el Excel si no hay errores previos
    if not guardar_excel(nuevo_registro):
        return
    
    #Mostramos un mensaje de éxito al usuario
    messagebox.showinfo("Éxito", "Fichaje guardado correctamente.")
    
    #limpiamos los campos del formulario
    limpiar_campos_formulario()

    #actualizamos el panel de control y el historico
    actualizar_todo()


def guardar_excel(registro):
    """Controlamos el guardado del registro en el Excel y manejamos posibles errores."""
    libro = None
    try:
        # Inicializamos el libro y la hoja de Excel, y agregamos el registro a la hoja y guardamos los cambios en el excel
        libro, hoja = inicializar_excel()
        hoja.append(registro)
        libro.save(Path(RUTA / NOMBRE_EXCEL))
        return True
    
    # Capturamos cualquier otro error que pueda ocurrir durante el guardado del Excel
    except PermissionError:
        print("Error: No se puede guardar el archivo de Excel. Está abierto en otro programa.")
        messagebox.showerror("Error", "No se puede guardar el archivo de Excel. Está abierto en otro programa.")
        return False
    except Exception as e:
        print(f"Error al guardar en el Excel: {e}")
        messagebox.showerror("Error", f"Error al guardar en el Excel: {e}")
        return False
    finally:
        if libro is not None:
            #por ultimo cerramos el libro de Excel
            libro.close()

def validacion_campos(id, nombre, departamento, tipo_accion):
    """Validamos todos los campos obligatorios uno por uno"""
    if not id:
        messagebox.showerror("Error", "El campo ID es obligatorio.")
        return False
    if not nombre:
        messagebox.showerror("Error", "El campo Nombre es obligatorio.")
        return False
    if not departamento:
        messagebox.showerror("Error", "El campo Departamento es obligatorio.")
        return False
    if not tipo_accion:
        messagebox.showerror("Error", "El campo Tipo de Registro es obligatorio.")
        return False
    #Validamos si las acciones del empleado son coherentes con su estado actual.
    registros = obtener_registros_excel()
    # Si no se pudieron obtener los registros, no se puede validar la acción.
    if registros is None:
        return False
    if not validar_id_empleado(id, nombre, departamento, registros):
        return False
    if not validar_accion(id, tipo_accion, registros):
        return False
    # TO DO validar los id del empleado con su nombre y departamento para no tener inconsistencias en los registros

    return True


def obtener_estado_empleado(id_empleado, registros):
    """Obtiene el estado actual del empleado según sus registros."""
    # Inicializamos el estado como "Fuera de turno" y lo actualizamos según los registros del empleado.
    estado = "Fuera de turno"
    for registro in registros:
        if str(registro[0].strip()) == str(id_empleado).strip():
            accion = registro[3]
            # Verificamos si la acción es válida para el estado actual y actualizamos el estado en consecuencia.
            if estado in ACCIONES and accion in ACCIONES[estado]:
                estado = ACCIONES[estado][accion]
    return estado

def validar_accion(id_empleado, accion, registros):
    """Valida si la acción es válida para el estado actual del empleado."""
    estado_actual = obtener_estado_empleado(id_empleado, registros)
    # Verificamos si la acción es válida para el estado actual del empleado.
    if estado_actual in ACCIONES and accion in ACCIONES[estado_actual]:
        return True
    # Si la acción no es válida, mostramos un mensaje de error y retornamos False.
    messagebox.showerror("Error", f"La acción '{accion}' no es válida para el estado actual '{estado_actual}'.")
    return False

def validar_id_empleado(id_empleado, nombre, departamento, registros):
    """Valida si el ID del empleado coincide con su nombre y departamento en los registros."""
    for registro in registros:
        if str(registro[0]).strip() == str(id_empleado).strip(): #Buscamos si el ID del empleado ya existe en los registros
            # Si encontramos el ID del empleado, verificamos que el nombre y departamento coincidan.
            if registro[1].strip().casefold() != nombre.strip().casefold():
                messagebox.showerror(
                    "Nombre incorrecto",
                    f"El ID '{id_empleado}' ya está asociado "
                    f"a otro empleado y no coincide con el nombre '{nombre}'."
                )
                return False

            if registro[2].strip() != departamento.strip():
                messagebox.showerror(
                    "Departamento incorrecto",
                    f"El empleado con ID '{id_empleado}' "
                    f"está registrado en otro departamento, "
                    f"no en '{departamento}'."
                )
                return False
    return True

def limpiar_campos_formulario():
    """Limpia los campos del formulario."""
    entry_id_empleado.delete(0, "end")
    entry_nombre_empleado.delete(0, "end")
    entry_departamento.set(entry_departamento['values'][0])
    entry_tipo_registro.set(entry_tipo_registro['values'][0])
    entry_observaciones.delete(0, "end")
    #Ponemos el foco en el campo ID del empleado para facilitar la entrada de datos
    entry_id_empleado.focus_set()

def obtener_registros_excel():
    """Obtenemos todos los registros del Excel."""
    libro = None
    try:
        libro, hoja = inicializar_excel()
        registros = list(hoja.iter_rows(min_row=2, values_only=True))
        libro.close()
        return registros
        
    except Exception as e:
        print(f"Error al obtener registros del Excel: {e}")
        messagebox.showerror("Error", f"Error al obtener registros del Excel: {e}")
        return None
    finally:
        if libro is not None:
            libro.close()

        
def calcular_registros_hoy(registros):
    """Calcula el total de empleados del día actual."""
    # Inicializamos el contador de registros del día actual por departamento
    fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
    empleados_hoy = set()
    #print(f"Registros: {registros}  Fecha actual: {fecha_actual}")
    for registro in registros:
        if registro[4] == fecha_actual and registro[0] is not None:  #la fecha está en la columna 5 (índice 4)
            empleados_hoy.add(registro[0])

    return len(empleados_hoy)

def calcular_departamentos(registros):
    """Calcula el número de departamentos distintos en los registros del dia actual."""
    fecha_actual = datetime.date.today().strftime("%d-%m-%Y")
    departamentos = set()
    
    for registro in registros:
        # Verificamos que la fecha sea la actual y que el campo de departamento no esté vacío
        if registro[4] == fecha_actual and registro[2]:
            departamentos.add(registro[2])
    
    return len(departamentos)
    
    
def actualizar_panel_control(registros = None):
    """Actualiza el panel de control con los registros proporcionados o los obtiene del Excel si no se proporcionan."""
    if registros is None:
        registros = obtener_registros_excel()
  
    if registros is None:
        return
  
    total_hoy = calcular_registros_hoy(registros)
    total_departamentos = calcular_departamentos(registros)
    
    total_registros.set(str(total_hoy))
    registros_departamento.set(str(total_departamentos))
    

def actualizar_historico(registros = None):
    """Actualiza el histórico con los registros proporcionados o los obtiene del Excel si no se proporcionan."""
    if registros is None:
        registros = obtener_registros_excel()
    
    if registros is None:
        return
    tabla_historico.build_table_data(coldata=columnas_historico, rowdata=registros)
    tabla_historico.load_table_data()
    print("Histórico actualizado.")
    
def actualizar_todo():
    """Actualiza tanto el panel de control como el histórico."""
    # Obtenemos los registros del Excel y actualizamos ambos paneles
    registros = obtener_registros_excel()
    if registros is None:
        return
    actualizar_panel_control(registros)
    actualizar_historico(registros)


#creamos la ventana principal de la aplicación
app = ttkb.Window(themename="cosmo")
app.geometry("1000x650")
app.minsize(850, 550)
app.title("Control Horario")
# Variables para el panel de control
total_registros = tk.StringVar(value="0")
registros_departamento = tk.StringVar(value="0")
# creamos las pestañas
pestana = ttkb.Notebook(app)
pestana.pack(expand=1, fill="both")

#Creamos el frame para registrar la jornada laboral y la configuramos
frame_registrar = ttkb.Frame(pestana, padding=15)
pestana.add(frame_registrar, text="Registrar")
frame_registrar.columnconfigure(0, weight=1)

#Creamos el frame para el panel de control
frame_panel_control = ttkb.Frame(pestana, padding=15)
pestana.add(frame_panel_control, text="Panel de Control")
# Configuramos las columnas del frame del panel de control para que se expandan igual
frame_panel_control.columnconfigure(0, weight=1)
frame_panel_control.columnconfigure(1, weight=1)

#Creamos el frame para el histórico
frame_historico = ttkb.Frame(pestana, padding=15)
pestana.add(frame_historico, text="Histórico")
# Configuramos las columnas y filas del frame del histórico para que se expandan correctamente
frame_historico.columnconfigure(0, weight=1)
frame_historico.rowconfigure(1, weight=1)

# 1 PESTAÑA REGISTRAR JORNADA LABORAL
titulo_registrar = ttkb.Label(frame_registrar, 
                              text="Registro de Jornada Laboral",
                              font=("Helvetica", 16, "bold"))
titulo_registrar.grid(column=0, row=0, sticky="w", pady=(0, 20))

frame_datos_empleado = ttkb.Labelframe(frame_registrar,
                                       text="Datos del Empleado",
                                       bootstyle="secondary",
                                       padding=15)
frame_datos_empleado.grid(column=0, row=1, sticky="ew", pady=(0, 15))    
# Configuramos la columna 1 para que se expanda y ocupe el espacio disponible
frame_datos_empleado.columnconfigure(1, weight=1)

#ID
label_id_empleado = ttkb.Label(frame_datos_empleado,
                               text="ID del Empleado:",
                               )
label_id_empleado.grid(column=0, row=0, sticky="w",padx=5, pady=10)

entry_id_empleado = ttkb.Entry(frame_datos_empleado,width=25)
entry_id_empleado.grid(column=1, row=0, sticky="w", padx=5, pady=10)

#Nombre Completo
label_nombre_empleado = ttkb.Label(frame_datos_empleado,
                                   text="Nombre Completo:")
label_nombre_empleado.grid(column=0, row=1, sticky="w", padx=5, pady=10)

entry_nombre_empleado = ttkb.Entry(frame_datos_empleado, width=40)
entry_nombre_empleado.grid(column=1, row=1, sticky="w", padx=5, pady=10)

#Departamento
label_departamento = ttkb.Label(frame_datos_empleado,
                                text="Departamento:")
label_departamento.grid(column=0, row=2, sticky="w", padx=5, pady=10)

entry_departamento = ttkb.Combobox(frame_datos_empleado,
                                   values=DEPARTAMENTOS,
                                   state="readonly", width=30)
entry_departamento.current(0)
entry_departamento.grid(column=1, row=2, sticky="w", padx=5, pady=10)

#Tipo de Registro
label_tipo_registro = ttkb.Label(frame_datos_empleado,
                                text="Tipo de Registro:")
label_tipo_registro.grid(column=0, row=3, sticky="w", padx=5, pady=10)

entry_tipo_registro = ttkb.Combobox(frame_datos_empleado,
                                    values=TIPOS_REGISTRO,
                                   state="readonly", width=30)
entry_tipo_registro.current(0)
entry_tipo_registro.grid(column=1, row=3, sticky="w", padx=5, pady=10)

#Observaciones
label_observaciones = ttkb.Label(frame_datos_empleado,
                                text="Observaciones:")
label_observaciones.grid(column=0, row=4, sticky="w", padx=5, pady=10)

entry_observaciones = ttkb.Entry(frame_datos_empleado, width=40)
entry_observaciones.grid(column=1, row=4, sticky="w", padx=5, pady=10)

#Botón Registrar Fichaje
registrar_button = ttkb.Button(frame_registrar,
                               text="Registrar Fichaje",
                               command=guardar_fichaje_excel,
                               bootstyle="success-outline",
                               width=25)
registrar_button.grid(column=0, row=2, padx=5, pady=10)


# 2 PESTAÑA PANEL DE CONTROL
titulo_panel_control = ttkb.Label(frame_panel_control, text="Panel de Control General", font=("Helvetica", 16, "bold"))
titulo_panel_control.grid(column=0, row=0, columnspan=2, sticky="w", pady=(0,15))
# Frame para mostrar el total de registros del día
frame_total_registros = ttkb.LabelFrame(frame_panel_control,
                                        text="Total Registros Hoy",
                                        bootstyle="info",
                                        padding=15)
frame_total_registros.grid(column=0, row=1, sticky="ew", padx=(0,5), pady=5)
label_total_registros = ttkb.Label(frame_total_registros, textvariable=total_registros, anchor="center")
label_total_registros.pack(fill="x", padx=5, pady=5)
# Frame para mostrar los registros por departamento
frame_registros_departamento = ttkb.LabelFrame(frame_panel_control,
                                               text="Departamentos involucrados",
                                               bootstyle="success",
                                               padding=15)
frame_registros_departamento.grid(column=1, row=1, sticky="ew", padx=(0,5), pady=5)
label_registros_departamento = ttkb.Label(frame_registros_departamento, textvariable=registros_departamento, anchor="center")
label_registros_departamento.pack(fill="x", padx=5, pady=5)
# Botón para actualizar el panel de control
boton_actualizar_panel_control = ttkb.Button(frame_panel_control, text="Actualizar Panel", command=actualizar_panel_control, bootstyle="secondary-outline", width=25)
boton_actualizar_panel_control.grid(column=0, row=2, columnspan=2, pady=15)

#PESTAÑA HISTORICO
titulo_historico = ttkb.Label(frame_historico, text="Histórico Registrado en Excel", font=("Helvetica", 16))
titulo_historico.grid(column=0, row=0, padx=5, pady=10, sticky="w")

columnas_historico = [
    {"text": "ID", "width": 70},
    {"text": "Nombre", "width": 150},
    {"text": "Departamento", "width": 170},
    {"text": "Acción", "width": 150},
    {"text": "Fecha", "width": 110},
    {"text": "Hora", "width": 90},
    {"text": "Observaciones", "width": 200}
]

tabla_historico = ttkb.Tableview(frame_historico,
                                coldata=columnas_historico,
                                rowdata=[],
                                paginated=True,
                                searchable=True,
                                bootstyle="primary",
                                stripecolor=("lightblue", None))
tabla_historico.grid(column=0, row=1, padx=5, pady=5, sticky="nsew")

boton_actualizar_historico = ttkb.Button(frame_historico, text="Actualizar Histórico",
                                         command=actualizar_historico,
                                         bootstyle="primary-outline",
                                         width=25)
boton_actualizar_historico.grid(column=0, row=2, padx=5, pady=10)


# Actualiza todos los paneles al iniciar la aplicación
actualizar_todo()

app.mainloop()

    