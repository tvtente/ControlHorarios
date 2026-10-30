import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox
from logica.gestor_fichajes import GestorFichajes
from excel.gestor_excel import GestorExcel
import interfaz.registrar as registrar
import interfaz.panel as panel
import interfaz.historico as historico
from config import  NOMBRE_EXCEL, COLUMNAS_EXCEL
from pathlib import Path

PATH = Path(__file__).resolve().parent
RUTA = PATH / NOMBRE_EXCEL

class App(ttkb.Window):
    def __init__(self, gestor_fichajes = None):
        super().__init__(themename="cosmo")
        self.gestor_fichajes = gestor_fichajes
        self.geometry("1200x650")
        self.minsize(1000, 650)
        self.title("Control Horario")
        
        pestanas = ttkb.Notebook(self)
        pestanas.pack(expand=True, fill="both")
        
        
        
        self.registrar = registrar.PestanaRegistrar(pestanas, self.guardar_fichaje)
        pestanas.add(self.registrar, text="Registrar Fichaje")
        
        self.panel = panel.PestanaPanel(pestanas, self.actualizar_panel)
        pestanas.add(self.panel, text="Panel de Control")
        
        self.historico = historico.PestanaHistorico(pestanas, self.actualizar_historico)
        pestanas.add(self.historico, text="Histórico")
        
        self.actualizar_todo()
        
    def guardar_fichaje(self):
        try:
            id, nombre, departamento, tipo, observaciones = self.registrar.obtener_datos()
            print(f"Obteniendo datos del fichaje: ID={id}, Nombre={nombre}, Departamento={departamento}, Tipo={tipo}, Observaciones={observaciones}")
            self.gestor_fichajes.registrar_fichaje(id, nombre, departamento, tipo, observaciones)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Éxito", "Fichaje registrado correctamente")
        self.registrar.limpiar_campos()
        self.actualizar_todo()
        
    def actualizar_panel(self, registros=None):
        if registros is None:
            registros = self.gestor_fichajes.gestor_excel.obtener_registros_excel()
        empleados = self.gestor_fichajes.calcular_empleados_hoy(registros)
        departamento = self.gestor_fichajes.calcular_departamentos(registros)
        print(f"empleados: {empleados}, departamento: {departamento}")
        self.panel.total_registros.set(str(empleados))
        self.panel.registros_departamento.set(str(departamento))

    def actualizar_historico(self, registros=None):
        if registros is None:
            registros = self.gestor_fichajes.gestor_excel.obtener_registros_excel()
        # Aquí puedes agregar la lógica para actualizar el histórico según tus necesidades
        self.historico.tabla.build_table_data(coldata=COLUMNAS_EXCEL, rowdata=registros)
        print(f"Actualizando histórico con registros: {registros}")

    def actualizar_todo(self):
        registros = self.gestor_fichajes.gestor_excel.obtener_registros_excel()
        self.actualizar_panel(registros)
        self.actualizar_historico(registros)

if __name__ == "__main__":
    excel = GestorExcel(ruta = RUTA, nombre_excel="control_horarios_viajes.xlsx")
    fichajes = GestorFichajes(excel)
    App(fichajes).mainloop()