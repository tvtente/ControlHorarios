import ttkbootstrap as ttkb
from config import COLUMNAS_EXCEL

class PestanaHistorico(ttkb.Frame):
    def __init__(self, master, actualizar):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        ttkb.Label(self, text="Histórico Registrado en Excel", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, padx=5, pady=10, sticky="w")
        
        self.tabla = ttkb.Tableview(
            self, coldata=COLUMNAS_EXCEL, rowdata=[], paginated=True,
            searchable=True, pagesize=8, bootstyle="primary",
            stripecolor=("lightblue", None),
        )
        self.tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        ttkb.Button(self, text="Actualizar Histórico", command=actualizar,
                    bootstyle="primary-outline", width=25).grid(row=2, column=0, pady=10)
