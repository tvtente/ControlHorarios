import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from repositorio_excel import RepositorioExcel
from servicio_fichajes import ServicioFichajes

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


class ControlHorariosApp:
    """Coordina la interfaz con las reglas de fichaje y el repositorio Excel."""

    def __init__(self, repositorio=None, servicio=None):
        self.repositorio = repositorio or RepositorioExcel(RUTA / NOMBRE_EXCEL)
        self.servicio = servicio or ServicioFichajes()

    def conectar_interfaz(self, ventana, id_empleado, nombre_empleado, departamento,
                          tipo_registro, observaciones, total_registros,
                          registros_departamento, columnas_historico, tabla_historico):
        self.ventana = ventana
        self.entry_id_empleado = id_empleado
        self.entry_nombre_empleado = nombre_empleado
        self.entry_departamento = departamento
        self.entry_tipo_registro = tipo_registro
        self.entry_observaciones = observaciones
        self.total_registros = total_registros
        self.registros_departamento = registros_departamento
        self.columnas_historico = columnas_historico
        self.tabla_historico = tabla_historico

    def obtener_datos_formulario(self):
        return (
            self.entry_id_empleado.get().strip(),
            self.entry_nombre_empleado.get().strip(),
            self.entry_departamento.get().strip(),
            self.entry_tipo_registro.get().strip(),
            self.entry_observaciones.get().strip(),
        )

    def guardar_fichaje_excel(self):
        try:
            id, nombre, departamento, tipo, observaciones = self.obtener_datos_formulario()
            registros = self.repositorio.obtener_registros_excel()
            nuevo_registro = self.servicio.crear_registro(
                id, nombre, departamento, tipo, observaciones, registros
            )
            self.repositorio.guardar_excel(nuevo_registro)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.ventana)
            return
        messagebox.showinfo("Éxito", "Fichaje guardado correctamente.", parent=self.ventana)
        self.limpiar_campos_formulario()
        self.actualizar_todo()

    def limpiar_campos_formulario(self):
        self.entry_id_empleado.delete(0, "end")
        self.entry_nombre_empleado.delete(0, "end")
        self.entry_departamento.set(DEPARTAMENTOS[0])
        self.entry_tipo_registro.set(TIPOS_REGISTRO[0])
        self.entry_observaciones.delete(0, "end")
        self.entry_id_empleado.focus_set()

    def obtener_registros_excel(self):
        try:
            return self.repositorio.obtener_registros_excel()
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo leer Excel", str(error), parent=self.ventana)
            return None

    def actualizar_panel_control(self, registros=None):
        if registros is None:
            registros = self.obtener_registros_excel()
        if registros is None:
            return
        self.total_registros.set(str(self.servicio.calcular_registros_hoy(registros)))
        self.registros_departamento.set(str(self.servicio.calcular_departamentos(registros)))

    def actualizar_historico(self, registros=None):
        if registros is None:
            registros = self.obtener_registros_excel()
        if registros is None:
            return
        self.tabla_historico.build_table_data(coldata=self.columnas_historico, rowdata=registros)
        self.tabla_historico.load_table_data()

    def actualizar_todo(self):
        registros = self.obtener_registros_excel()
        if registros is None:
            return
        self.actualizar_panel_control(registros)
        self.actualizar_historico(registros)

controlador = ControlHorariosApp()
guardar_fichaje_excel = controlador.guardar_fichaje_excel
actualizar_panel_control = controlador.actualizar_panel_control
actualizar_historico = controlador.actualizar_historico
actualizar_todo = controlador.actualizar_todo


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


# Conecta los widgets creados con el controlador orientado a objetos.
controlador.conectar_interfaz(
    app, entry_id_empleado, entry_nombre_empleado, entry_departamento,
    entry_tipo_registro, entry_observaciones, total_registros,
    registros_departamento, columnas_historico, tabla_historico,
)

# Actualiza todos los paneles al iniciar la aplicación
actualizar_todo()

app.mainloop()

    