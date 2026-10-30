"""Tercera pestaña: tabla de registros guardados en Excel."""

import ttkbootstrap as ttkb


class PestanaHistorico(ttkb.Frame):
    columnas_historico = [
        {"text": "ID", "width": 70},
        {"text": "Nombre", "width": 150},
        {"text": "Departamento", "width": 170},
        {"text": "Acción", "width": 150},
        {"text": "Fecha", "width": 110},
        {"text": "Hora", "width": 90},
        {"text": "Observaciones", "width": 200},
    ]

    def __init__(self, master=None, actualizar_historico=None):
        super().__init__(master, padding=15)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttkb.Label(self, text="Histórico Registrado en Excel",
                   font=("Helvetica", 16)).grid(
                       column=0, row=0, padx=5, pady=10, sticky="w")

        self.tabla_historico = ttkb.Tableview(
            self, coldata=self.columnas_historico, rowdata=[], paginated=True,
            searchable=True, bootstyle="primary", stripecolor=("lightblue", None))
        self.tabla_historico.grid(column=0, row=1, padx=5, pady=5, sticky="nsew")

        ttkb.Button(self, text="Actualizar Histórico", command=actualizar_historico,
                    bootstyle="primary-outline", width=25).grid(
                        column=0, row=2, padx=5, pady=10)

    def mostrar(self, registros):
        self.tabla_historico.build_table_data(
            coldata=self.columnas_historico, rowdata=registros)
        self.tabla_historico.load_table_data()
