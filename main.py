"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import pygubu

from excel_manager import ExcelManager


UI_FILE = Path(__file__).resolve().parent / "ui" / "control_horarios.ui"


class ControlHorariosApp:
    """Carga el diseño y controla la interfaz gráfica de la aplicación."""

    def __init__(self):
        carpeta_datos = Path(__file__).resolve().parent / "data"
        carpeta_datos.mkdir(parents=True, exist_ok=True)
        self.excel = ExcelManager(carpeta_datos / "control_horarios_viajes.xlsx")
        self.ventana = tk.Tk()
        self.ventana.title("Control de horarios")
        self.ventana.geometry("1100x750")
        self.builder = pygubu.Builder()
        self.builder.add_from_file(str(UI_FILE))
        self.interfaz = self.builder.get_object("app", self.ventana)
        self.interfaz.pack(fill="both", expand=True)
        self.builder.connect_callbacks(self)
        for origen, destino in (("departamento", "filtro_departamento"), ("accion", "filtro_accion")):
            self.builder.get_object(destino).configure(
                values=self.builder.get_object(origen).cget("values")
            )
        self.consultar_registros()

    # Métodos de la interfaz gráfica.

    def run(self):
        """Inicia el bucle de eventos de la ventana."""
        self.ventana.mainloop()

    def limpiar_formulario(self):
        """Vacía los campos del formulario de registro."""
        for nombre in (
            "id_empleado", "nombre_completo", "hora_inicio_prevista",
            "hora_fin_prevista", "observaciones",
        ):
            self.builder.get_object(nombre).delete(0, tk.END)
        for nombre in ("departamento", "accion"):
            self.builder.get_object(nombre).set("")
        self.builder.get_object("id_empleado").focus_set()

    def limpiar_filtros(self):
        """Restablece los filtros y vuelve a mostrar todos los registros."""
        self.builder.get_object("buscar_empleado").delete(0, tk.END)
        for nombre in ("filtro_departamento", "filtro_accion"):
            self.builder.get_object(nombre).set("")
        self.consultar_registros()

    def actualizar_historico(self):
        """Recarga la tabla del histórico utilizando los filtros actuales."""
        self.consultar_registros()

    # Métodos que conectan la interfaz con el manejo de Excel.

    def guardar_registro(self):
        """Recoge los campos y llama a self.excel.guardar_registro(...)."""
        campos = (
            "id_empleado", "nombre_completo", "departamento", "accion",
            "observaciones", "hora_inicio_prevista", "hora_fin_prevista",
        )
        datos = {nombre: self.builder.get_object(nombre).get() for nombre in campos}
        try:
            self.excel.guardar_registro(**datos)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.ventana)
            return
        self.limpiar_formulario()
        self.builder.get_object("estado_registro").configure(text="Registro guardado correctamente")
        self.actualizar_historico()

    def consultar_registros(self):
        """Recoge los filtros, consulta self.excel y actualiza la tabla."""
        try:
            registros = self.excel.consultar_registros(
                empleado=self.builder.get_object("buscar_empleado").get(),
                departamento=self.builder.get_object("filtro_departamento").get(),
                accion=self.builder.get_object("filtro_accion").get(),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo consultar", str(error), parent=self.ventana)
            return
        tabla = self.builder.get_object("tabla_fichajes")
        columnas = (
            "id_registro", "id_empleado", "nombre_completo", "departamento",
            "accion", "fecha", "hora", "hora_inicio_prevista",
            "hora_fin_prevista", "observaciones",
        )
        # Solo se reemplazan las filas visibles; los datos del Excel se conservan.
        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)
        for registro in registros:
            tabla.insert("", "end", values=[
                registro.get(columna) if registro.get(columna) is not None else ""
                for columna in columnas
            ])


if __name__ == "__main__":
    ControlHorariosApp().run()
