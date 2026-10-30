import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox
from logica.gestor_fichajes import GestorFichajes
from excel.gestor_excel import GestorExcel
import interfaz.registrar as registrar
import interfaz.panel as panel

class App(ttkb.Window):
    def __init__(self, gestor_fichajes = None):
        super().__init__(themename="cosmo")
        self.gestor_fichajes = gestor_fichajes or GestorFichajes(GestorExcel())
        self.geometry("1000x650")
        self.minsize(1000, 650)
        self.title("Control Horario")
        
        pestanas = ttkb.Notebook(self)
        pestanas.pack(expand=True, fill="both")
        
        
        
        self.registrar = registrar.PestanaRegistrar(pestanas, self.guardar_fichaje)
        pestanas.add(self.registrar, text="Registrar Fichaje")

        self.panel_control = panel.PestanaPanel(pestanas, self.actualizar_panel_control)
        pestanas.add(self.panel_control, text="Panel de Control")
        self.actualizar_panel_control()
        
    def guardar_fichaje(self):
        try:
            id, nombre, departamento, tipo, observaciones = self.registrar.obtener_datos()
            self.gestor_fichajes.registrar_fichaje(id, nombre, departamento, tipo, observaciones)
        except (ValueError, OSError) as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
            
        messagebox.showinfo("Éxito", "Fichaje registrado correctamente")
        self.registrar.limpiar_campos()
        self.actualizar_panel_control()

    def actualizar_panel_control(self):
        try:
            registros = self.gestor_fichajes.gestor_excel.obtener_registros_excel()
        except (ValueError, OSError) as e:
            messagebox.showerror("Error al actualizar panel", str(e), parent=self)
            return
        self.panel_control.total_registros.set(
            str(self.gestor_fichajes.calcular_empleados_hoy(registros))
        )
        self.panel_control.registros_departamento.set(
            str(self.gestor_fichajes.calcular_departamentos(registros))
        )
        
    
if __name__ == "__main__":
    App().mainloop()
