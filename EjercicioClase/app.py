"""Aplicación principal: reúne dos pestañas diseñadas en archivos UI distintos."""

from pathlib import Path
import tkinter as tk

import pygubu
import ttkbootstrap as ttkb

if __package__:
    from .formulario import PestanaFormulario
    from .styles import TEMA, configurar_estilos
    from .tabla import PestanaTabla
else:
    from formulario import PestanaFormulario
    from styles import TEMA, configurar_estilos
    from tabla import PestanaTabla

CARPETA = Path(__file__).resolve().parent
UI_DIR = CARPETA / "ui"
IMAGES_DIR = CARPETA / "images"


class DemoPygubu:
    def __init__(self):
        self.ventana = ttkb.Window(themename=TEMA)
        self.ventana.title("Ejercicio de clase · Pygubu")
        self.ventana.geometry("850x650")
        self.ventana.minsize(800, 550)
        self._icono = tk.PhotoImage(file=str(IMAGES_DIR / "icono.png"))
        self.ventana.iconphoto(True, self._icono)
        configurar_estilos(self.ventana)

        # Primer Builder: estructura general y contenedores de las pestañas.
        self.builder = pygubu.Builder()
        self.builder.add_from_file(str(UI_DIR / "principal.ui"))
        self.aplicacion = self.builder.get_object("aplicacion", self.ventana)
        self.aplicacion.pack(fill="both", expand=True)

        # Cada clase carga su propio archivo UI en el contenedor correspondiente.
        self.formulario = PestanaFormulario(
            self.builder.get_object("contenedor_formulario"), self.guardar_persona
        )
        self.tabla = PestanaTabla(
            self.builder.get_object("contenedor_tabla"), self.eliminar_persona
        )
        self.builder.connect_callbacks(self)

        # Los datos pertenecen a la aplicación, no a ninguna de las pestañas.
        self.personas = []
        self.siguiente_id = 1
        self.tabla.mostrar_personas(self.personas)

    def guardar_persona(self, datos):
        persona = {"id": self.siguiente_id, **datos}
        self.personas.append(persona)
        self.siguiente_id += 1
        self.tabla.mostrar_personas(self.personas)
        self.builder.get_object("pestanas").select(1)

    def eliminar_persona(self, id_elegido):
        self.personas = [p for p in self.personas if p["id"] != id_elegido]
        self.tabla.mostrar_personas(self.personas)

    def al_cambiar_pestana(self, _evento=None):
        """Binding del Notebook declarado en principal.ui."""
        if self.builder.get_object("pestanas").index("current") == 1:
            self.tabla.mostrar_personas(self.personas)

    def run(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    DemoPygubu().run()
