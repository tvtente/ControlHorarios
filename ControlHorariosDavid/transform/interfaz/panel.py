"""Segunda pestaña: indicadores del día."""

import tkinter as tk

import ttkbootstrap as ttkb


class PestanaPanel(ttkb.Frame):
    def __init__(self, master=None, actualizar_panel_control=None):
        super().__init__(master, padding=15)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.total_registros = tk.StringVar(master=self, value="0")
        self.registros_departamento = tk.StringVar(master=self, value="0")

        ttkb.Label(self, text="Panel de Control General",
                   font=("Helvetica", 16, "bold")).grid(
                       column=0, row=0, columnspan=2, sticky="w", pady=(0, 15))
        for columna, (titulo, estilo, variable) in enumerate((
            ("Total Registros Hoy", "info", self.total_registros),
            ("Departamentos involucrados", "success", self.registros_departamento),
        )):
            marco = ttkb.LabelFrame(self, text=titulo, bootstyle=estilo, padding=15)
            marco.grid(column=columna, row=1, sticky="ew", padx=(0, 5), pady=5)
            ttkb.Label(marco, textvariable=variable, anchor="center").pack(
                fill="x", padx=5, pady=5)

        ttkb.Button(self, text="Actualizar Panel", command=actualizar_panel_control,
                    bootstyle="secondary-outline", width=25).grid(
                        column=0, row=2, columnspan=2, pady=15)

    def mostrar(self, empleados_hoy, departamentos):
        self.total_registros.set(str(empleados_hoy))
        self.registros_departamento.set(str(departamentos))
