"""Controlador de la pestaña Formulario y su archivo formulario.ui."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import pygubu

IMAGES_DIR = Path(__file__).with_name("images")
INTERVALO_GIF_MS = 650


class PestanaFormulario:
    def __init__(self, contenedor, al_guardar):
        self.al_guardar = al_guardar
        self.builder = pygubu.Builder()
        self.builder.add_resource_path(str(IMAGES_DIR))
        self.builder.add_from_file(str(Path(__file__).with_name("ui") / "formulario.ui"))
        self.pantalla = self.builder.get_object("pantalla_formulario", contenedor)
        self.pantalla.pack(fill="both", expand=True)
        self.builder.connect_callbacks(self)

        self.turno = tk.StringVar(master=self.pantalla, value="Mañana")
        self.activo = tk.BooleanVar(master=self.pantalla, value=True)
        for nombre in ("turno_manana", "turno_tarde"):
            self.campo(nombre).configure(variable=self.turno)
        self.campo("activo").configure(variable=self.activo)
        self.campo("categoria").set("General")
        self.campo("edad").set("18")
        self._iniciar_animacion()

    def _iniciar_animacion(self):
        """Tk carga un fotograma del GIF por índice; after los va alternando."""
        archivo = IMAGES_DIR / "registro_animado.gif"
        self._fotogramas = []
        indice = 0
        while True:
            try:
                fotograma = tk.PhotoImage(master=self.pantalla, file=str(archivo),
                                         format=f"gif -index {indice}")
            except tk.TclError:
                break
            self._fotogramas.append(fotograma)
            indice += 1
        if not self._fotogramas:
            raise ValueError(f"El GIF no tiene fotogramas: {archivo}")
        self._fotograma_actual = 0
        self._temporizador = None
        self._mostrar_siguiente_fotograma()

    def _mostrar_siguiente_fotograma(self):
        self.campo("imagen_animada").configure(
            image=self._fotogramas[self._fotograma_actual]
        )
        self._fotograma_actual = (self._fotograma_actual + 1) % len(self._fotogramas)
        self._temporizador = self.pantalla.after(
            INTERVALO_GIF_MS, self._mostrar_siguiente_fotograma
        )

    def detener_animacion(self, _evento=None):
        """Binding Destroy del Label, declarado en formulario.ui."""
        if getattr(self, "_temporizador", None) is not None:
            self.pantalla.after_cancel(self._temporizador)
            self._temporizador = None

    def campo(self, nombre):
        return self.builder.get_object(nombre)

    def leer_datos(self):
        """Devuelve los valores del formulario, o avisa si faltan datos."""
        nombre = self.campo("nombre").get().strip()
        if not nombre:
            messagebox.showwarning("Falta un dato", "Escribe un nombre.", parent=self.pantalla)
            self.campo("nombre").focus_set()
            return None
        try:
            edad = int(self.campo("edad").get())
        except ValueError:
            edad = -1
        if not 0 <= edad <= 120:
            messagebox.showwarning("Edad incorrecta", "Introduce una edad entre 0 y 120.", parent=self.pantalla)
            self.campo("edad").focus_set()
            return None
        return {
            "nombre": nombre,
            "categoria": self.campo("categoria").get(),
            "edad": edad,
            "turno": self.turno.get(),
            "activo": self.activo.get(),
            "notas": self.campo("notas").get("1.0", "end-1c").strip(),
        }

    def guardar_persona(self):
        """Callback del botón definido en formulario.ui."""
        datos = self.leer_datos()
        if datos is not None:
            self.al_guardar(datos)
            self.limpiar_formulario()

    def limpiar_formulario(self):
        self.campo("nombre").delete(0, tk.END)
        self.campo("categoria").set("General")
        self.campo("edad").set("18")
        self.turno.set("Mañana")
        self.activo.set(True)
        self.campo("notas").delete("1.0", tk.END)
        self.campo("nombre").focus_set()

    def cambio_categoria(self, _evento=None):
        """Callback del binding ComboboxSelected definido en formulario.ui."""
        self.campo("titulo").configure(
            text=f"Registro de personas · {self.campo('categoria').get()}"
        )
