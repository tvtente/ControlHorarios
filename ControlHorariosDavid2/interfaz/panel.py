import tkinter as tk
import ttkbootstrap as ttkb

class PestanaPanel(ttkb.Frame):
    def __init__(self, master, actualizar):
        super().__init__(master)
        self.total_registros = tk.StringVar(self, value="0")
        self.registros_departamento = tk.StringVar(self, value="0")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        #Titulo
        ttkb.Label(self, text="Panel de Control General", font=("Helvetica", 16, "bold")
                   ).grid(row=0, column=0, columnspan=2, sticky="w",padx=5, pady=10)
        #Frames
        frame_empleados = ttkb.Labelframe(self, text="Total Registros Hoy", bootstyle="info", padding=15)
        frame_empleados.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=5)
        ttkb.Label(frame_empleados, textvariable=self.total_registros,
                    font=("Helvetica", 28, "bold"), anchor="center").pack(fill="x", pady=5)

        frame_departamento = ttkb.Labelframe(self, text="Registros por Departamento", bootstyle="success", padding=15)
        frame_departamento.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=5)
        ttkb.Label(frame_departamento, textvariable=self.registros_departamento,
                    font=("Helvetica", 28, "bold"), anchor="center").pack(fill="x", pady=5)
        
        #Boton
        ttkb.Button(self, text="Actualizar Panel", command=actualizar,
                    bootstyle="secondary-outline", width=25).grid(row=2, column=0, columnspan=2, pady=15)
    