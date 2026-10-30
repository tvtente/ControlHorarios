"""Primera pestaña: formulario de registro."""

import ttkbootstrap as ttkb

from config import DEPARTAMENTOS, TIPOS_REGISTRO


class PestanaRegistrar(ttkb.Frame):
    def __init__(self, master=None, guardar_fichaje_excel=None):
        super().__init__(master, padding=15)
        self.columnconfigure(0, weight=1)

        ttkb.Label(self, text="Registro de Jornada Laboral",
                   font=("Helvetica", 16, "bold")).grid(
                       column=0, row=0, sticky="w", pady=(0, 20))

        frame_datos_empleado = ttkb.Labelframe(
            self, text="Datos del Empleado", bootstyle="secondary", padding=15)
        frame_datos_empleado.grid(column=0, row=1, sticky="ew", pady=(0, 15))
        frame_datos_empleado.columnconfigure(1, weight=1)

        campos = (
            ("ID del Empleado:", "entry_id_empleado", ttkb.Entry, {"width": 25}),
            ("Nombre Completo:", "entry_nombre_empleado", ttkb.Entry, {"width": 40}),
            ("Departamento:", "entry_departamento", ttkb.Combobox,
             {"values": DEPARTAMENTOS, "state": "readonly", "width": 30}),
            ("Tipo de Registro:", "entry_tipo_registro", ttkb.Combobox,
             {"values": TIPOS_REGISTRO, "state": "readonly", "width": 30}),
            ("Observaciones:", "entry_observaciones", ttkb.Entry, {"width": 40}),
        )
        for fila, (etiqueta, nombre, clase, opciones) in enumerate(campos):
            ttkb.Label(frame_datos_empleado, text=etiqueta).grid(
                column=0, row=fila, sticky="w", padx=5, pady=10)
            campo = clase(frame_datos_empleado, **opciones)
            campo.grid(column=1, row=fila, sticky="w", padx=5, pady=10)
            setattr(self, nombre, campo)

        self.entry_departamento.current(0)
        self.entry_tipo_registro.current(0)
        ttkb.Button(self, text="Registrar Fichaje", command=guardar_fichaje_excel,
                    bootstyle="success-outline", width=25).grid(
                        column=0, row=2, padx=5, pady=10)

    def obtener_datos_formulario(self):
        return (
            self.entry_id_empleado.get().strip(),
            self.entry_nombre_empleado.get().strip(),
            self.entry_departamento.get().strip(),
            self.entry_tipo_registro.get().strip(),
            self.entry_observaciones.get().strip(),
        )

    def limpiar_campos_formulario(self):
        self.entry_id_empleado.delete(0, "end")
        self.entry_nombre_empleado.delete(0, "end")
        self.entry_departamento.current(0)
        self.entry_tipo_registro.current(0)
        self.entry_observaciones.delete(0, "end")
        self.entry_id_empleado.focus_set()
