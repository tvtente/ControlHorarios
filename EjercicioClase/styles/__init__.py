"""Estilos compartidos por las dos pestañas de la demostración."""

from tkinter import ttk


TEMA = "flatly"


def configurar_estilos(ventana):
    estilos = ttk.Style(ventana)
    estilos.configure("DemoTitulo.TLabel", font=("Helvetica", 16, "bold"))
    estilos.configure("DemoEstado.TLabel", foreground="#4B5563")
