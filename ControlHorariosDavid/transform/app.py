"""Punto de entrada de la versión separada en clases."""

from tkinter import messagebox

import ttkbootstrap as ttkb

from excel.gestor_excel import GestorExcel
from interfaz.historico import PestanaHistorico
from interfaz.panel import PestanaPanel
from interfaz.registrar import PestanaRegistrar
from logica.gestor_fichajes import GestorFichajes


class App(ttkb.Window):
    def __init__(self, gestor_fichajes=None):
        super().__init__(themename="cosmo")
        self.gestor_excel = (gestor_fichajes.gestor_excel if gestor_fichajes
                             else GestorExcel())
        self.gestor_fichajes = gestor_fichajes or GestorFichajes(self.gestor_excel)
        self.geometry("1000x650")
        self.minsize(850, 550)
        self.title("Control Horario")

        pestanas = ttkb.Notebook(self)
        pestanas.pack(expand=True, fill="both")

        self.registrar = PestanaRegistrar(pestanas, self.guardar_fichaje_excel)
        pestanas.add(self.registrar, text="Registrar")
        self.panel_control = PestanaPanel(pestanas, self.actualizar_panel_control)
        pestanas.add(self.panel_control, text="Panel de Control")
        self.historico = PestanaHistorico(pestanas, self.actualizar_historico)
        pestanas.add(self.historico, text="Histórico")

        self.actualizar_todo()

    def guardar_fichaje_excel(self):
        try:
            datos = self.registrar.obtener_datos_formulario()
            self.gestor_fichajes.guardar_fichaje_excel(*datos)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self)
            return
        messagebox.showinfo("Éxito", "Fichaje guardado correctamente.", parent=self)
        self.registrar.limpiar_campos_formulario()
        self.actualizar_todo()

    def obtener_registros_excel(self):
        try:
            return self.gestor_excel.obtener_registros_excel()
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo leer Excel", str(error), parent=self)
            return None

    def actualizar_panel_control(self, registros=None):
        if registros is None:
            registros = self.obtener_registros_excel()
        if registros is None:
            return
        self.panel_control.mostrar(
            self.gestor_fichajes.calcular_empleados_hoy(registros),
            self.gestor_fichajes.calcular_departamentos(registros),
        )

    def actualizar_historico(self, registros=None):
        if registros is None:
            registros = self.obtener_registros_excel()
        if registros is not None:
            self.historico.mostrar(registros)

    def actualizar_todo(self):
        registros = self.obtener_registros_excel()
        if registros is None:
            return
        self.actualizar_panel_control(registros)
        self.actualizar_historico(registros)


if __name__ == "__main__":
    App().mainloop()
