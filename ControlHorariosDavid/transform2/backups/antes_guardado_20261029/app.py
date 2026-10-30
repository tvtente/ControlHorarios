import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox
from logica.gestor_fichajes import GestorFichajes
from excel.gestor_excel import GestorExcel
import interfaz.registrar as registrar

class App(ttkb.Window):
    def __init__(self, gestor_fichajes = None):
        super().__init__(themename="cosmo")
        self.gestor_fichajes = gestor_fichajes
        self.geometry("1000x650")
        self.minsize(1000, 650)
        self.title("Control Horario")
        
        pestanas = ttkb.Notebook(self)
        pestanas.pack(expand=True, fill="both")
        
        
        
        self.registrar = registrar.PestanaRegistrar(pestanas, self.guardar_fichaje)
        pestanas.add(self.registrar, text="Registrar Fichaje")
        
    def guardar_fichaje(self):
        try:
            id, nombre, departamento, tipo, observaciones = self.registrar.obtener_datos()
            self.gestor_fichajes.registrar_fichaje(id, nombre, departamento, tipo, observaciones)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
        messagebox.showinfo("Éxito", "Fichaje registrado correctamente")
        self.registrar.limpiar_campos()
        
    
if __name__ == "__main__":
    excel = GestorExcel("ControlHorariosDavid/transform2/archivos/fichajes.xlsx")
    gestor_fichajes = GestorFichajes(excel)
    App().mainloop()