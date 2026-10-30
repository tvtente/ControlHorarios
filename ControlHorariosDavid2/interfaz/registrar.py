import ttkbootstrap as ttkb
from config import DEPARTAMENTOS, TIPOS_REGISTRO

class PestanaRegistrar(ttkb.Frame):
    def __init__(self, master=None, guardar_fichaje_excel=None ):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        ttkb.Label(self, text="Registro de Jornada Laboral",
                        font=("Helvetica", 16, "bold")
                        ).grid(row=0, column=0,padx=5, pady=10, sticky="w")
        datos = ttkb.Labelframe(self,
                                       text="Datos del Empleado",
                                       bootstyle="secondary",
                                       padding=15)
        datos.grid(column=0, row=1, sticky="ew", pady=(0, 15))
        datos.columnconfigure(1, weight=1)
        
        # Frame para los datos del empleado
        self.label_id_empleado = ttkb.Label(datos,
                               text="ID del Empleado:",
                               )
        self.label_id_empleado.grid(column=0, row=0, sticky="w",padx=5, pady=10)

        self.entry_id_empleado = ttkb.Entry(datos,width=25)
        self.entry_id_empleado.grid(column=1, row=0, sticky="w", padx=5, pady=10)

        #Nombre Completo
        self.label_nombre_empleado = ttkb.Label(datos,
                                        text="Nombre Completo:")
        self.label_nombre_empleado.grid(column=0, row=1, sticky="w", padx=5, pady=10)

        self.entry_nombre_empleado = ttkb.Entry(datos, width=40)
        self.entry_nombre_empleado.grid(column=1, row=1, sticky="w", padx=5, pady=10)

        #Departamento
        self.label_departamento = ttkb.Label(datos,
                                        text="Departamento:")
        self.label_departamento.grid(column=0, row=2, sticky="w", padx=5, pady=10)

        self.entry_departamento = ttkb.Combobox(datos,
                                        values=DEPARTAMENTOS,
                                        state="readonly", width=30)
        self.entry_departamento.current(0)
        self.entry_departamento.grid(column=1, row=2, sticky="w", padx=5, pady=10)

        #Tipo de Registro
        self.label_tipo_registro = ttkb.Label(datos,
                                        text="Tipo de Registro:")
        self.label_tipo_registro.grid(column=0, row=3, sticky="w", padx=5, pady=10)

        self.entry_tipo_registro = ttkb.Combobox(datos,
                                            values=TIPOS_REGISTRO,
                                        state="readonly", width=30)
        self.entry_tipo_registro.current(0)
        self.entry_tipo_registro.grid(column=1, row=3, sticky="w", padx=5, pady=10)

        #Observaciones
        self.label_observaciones = ttkb.Label(datos,
                                        text="Observaciones:")
        self.label_observaciones.grid(column=0, row=4, sticky="w", padx=5, pady=10)

        self.entry_observaciones = ttkb.Entry(datos, width=40)
        self.entry_observaciones.grid(column=1, row=4, sticky="w", padx=5, pady=10)

        #Botón Registrar Fichaje
        self.registrar_button = ttkb.Button(datos,
                                    text="Registrar Fichaje",
                                    command=guardar_fichaje_excel,
                                    bootstyle="success-outline",
                                    width=25)
        self.registrar_button.grid(column=0, row=5, columnspan=2, padx=5, pady=10)    
        
    def obtener_datos(self):
        id_empleado = self.entry_id_empleado.get().strip()
        nombre_empleado = self.entry_nombre_empleado.get().strip()
        departamento = self.entry_departamento.get().strip()
        tipo_registro = self.entry_tipo_registro.get().strip()
        observaciones = self.entry_observaciones.get().strip()
        return id_empleado, nombre_empleado, departamento, tipo_registro, observaciones
    
    def limpiar_campos(self):
        self.entry_id_empleado.delete(0, "end")
        self.entry_nombre_empleado.delete(0, "end")
        self.entry_departamento.current(0)
        self.entry_tipo_registro.current(0)
        self.entry_observaciones.delete(0, "end")
        self.entry_id_empleado.focus_set()