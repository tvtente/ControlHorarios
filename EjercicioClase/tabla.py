"""Controlador de la pestaña Tabla y su archivo tabla.ui."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import pygubu


class PestanaTabla:
    def __init__(self, contenedor, al_eliminar):
        self.al_eliminar = al_eliminar
        self.personas = []
        self.builder = pygubu.Builder()
        self.builder.add_from_file(str(Path(__file__).with_name("ui") / "tabla.ui"))
        self.pantalla = self.builder.get_object("pantalla_tabla", contenedor)
        self.pantalla.pack(fill="both", expand=True)
        self.builder.connect_callbacks(self)
        self.actualizar_tabla()

    def campo(self, nombre):
        return self.builder.get_object(nombre)

    def mostrar_personas(self, personas):
        """Recibe los datos de la aplicación y refresca la vista."""
        self.personas = personas
        self.actualizar_tabla()

    def filtrar_tabla(self, _evento=None):
        """Callback de KeyRelease, declarado en tabla.ui."""
        self.actualizar_tabla()

    def seleccionar_persona(self, _evento=None):
        seleccion = self.campo("tabla").selection()
        if seleccion:
            self.campo("estado").configure(text=f"Fila seleccionada: ID {seleccion[0]}")

    def eliminar_persona(self):
        seleccion = self.campo("tabla").selection()
        if not seleccion:
            messagebox.showinfo("Selecciona una fila", "Elige una persona en la tabla.", parent=self.pantalla)
            return
        self.al_eliminar(int(seleccion[0]))

    def actualizar_tabla(self):
        tabla = self.campo("tabla")
        tabla.delete(*tabla.get_children())
        busqueda = self.campo("buscar").get().strip().casefold()
        visibles = 0
        for persona in self.personas:
            if busqueda and busqueda not in persona["nombre"].casefold() \
                    and busqueda not in persona["categoria"].casefold():
                continue
            tabla.insert("", tk.END, iid=str(persona["id"]), values=(
                persona["id"], persona["nombre"], persona["categoria"],
                persona["edad"], persona["turno"],
                "Sí" if persona["activo"] else "No", persona["notas"],
            ))
            visibles += 1
        total = len(self.personas)
        self.campo("estado").configure(text=f"{visibles} visibles de {total} personas")
        self.campo("progreso").configure(value=min(total, 10))
