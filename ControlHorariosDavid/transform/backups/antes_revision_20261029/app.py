import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox

class App(ttkb.Window):
    def __init__(self, gestor_fichajes):
        super().__init__(themename="cosmo")
        self.gestor_fichajes = gestor_fichajes
        self.geometry("1000x650")
        self.minsize(1000, 650)
        self.title("Control Horario")
        
        pestanas = ttkb.Notebook(self)
        pestanas.pack(expand=True, fill="both")
        
        self.registrar = ttkb.Frame(pestanas)
        pestanas.add(self.registrar, text="Registrar Fichaje")
        
        self.panel_control = ttkb.Frame(pestanas)
        pestanas.add(self.panel_control, text="Panel de Control")
        
        self.historico = ttkb.Frame(pestanas)
        pestanas.add(self.historico, text="Histórico")
        
        