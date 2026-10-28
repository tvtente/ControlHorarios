"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

import pygubu
import ttkbootstrap as tb

from dashboard import build_dashboard_data, dibujar_departamentos, dibujar_fichajes_por_dia
from excel_manager import ExcelManager
from styles import TEMA, aplicar_estilos_widgets, configurar_estilos, configurar_estilos_panel


UI_DIR = Path(__file__).resolve().parent / "ui"
UI_FILE = UI_DIR / "control_horarios.ui"


class ConstructoresPygubu:
    """Expone los widgets y callbacks de los cuatro archivos UI como un conjunto."""

    def __init__(self, constructores):
        self.constructores = constructores
        self.por_nombre = {}
        for constructor in constructores:
            for nombre in constructor.objects:
                if nombre in self.por_nombre:
                    raise ValueError(f"ID de widget repetido entre archivos UI: {nombre}")
                self.por_nombre[nombre] = constructor

    def get_object(self, nombre):
        if nombre not in self.por_nombre:
            raise KeyError(f"No existe el widget de Pygubu: {nombre}")
        return self.por_nombre[nombre].get_object(nombre)

    def connect_callbacks(self, controlador):
        for constructor in self.constructores:
            constructor.connect_callbacks(controlador)


class ControlHorariosApp:
    """Carga el diseño y controla la interfaz gráfica de la aplicación."""

    def __init__(self):
        carpeta_datos = Path(__file__).resolve().parent / "data"
        carpeta_datos.mkdir(parents=True, exist_ok=True)

        self.excel = ExcelManager(
            carpeta_datos / "control_horarios_viajes.xlsx"
        )

        self.ventana = tb.Window(themename=TEMA)
        self.ventana.title("Control de horarios")
        self.ventana.geometry("1280x800")
        self.ventana.minsize(1000, 650)

        configurar_estilos(self.ventana)

        general = pygubu.Builder()
        general.add_from_file(str(UI_FILE))
        self.interfaz = general.get_object("app", self.ventana)
        self.interfaz.pack(fill="both", expand=True)

        constructores = [general]
        for nombre in ("registro", "panel", "historico"):
            constructor = pygubu.Builder()
            constructor.add_from_file(str(UI_DIR / f"{nombre}.ui"))
            contenedor = general.get_object(f"contenedor_{nombre}")
            pantalla = constructor.get_object(f"pantalla_{nombre}", contenedor)
            pantalla.pack(fill="both", expand=True)
            constructores.append(constructor)

        self.builder = ConstructoresPygubu(constructores)

        self.builder.connect_callbacks(self)
        aplicar_estilos_widgets(self.ventana, self.builder)

        # Copy department and action options into the history filters.
        for origen, destino in (
            ("departamento", "filtro_departamento"),
            ("accion", "filtro_accion"),
        ):
            self.builder.get_object(destino).configure(
                values=self.builder.get_object(origen).cget("values")
            )

        self.configurar_panel()
        self.consultar_registros()

    # Methods connected to the graphical interface

    def run(self):
        """Inicia el bucle de eventos de la ventana."""
        self.ventana.mainloop()

    def limpiar_formulario(self):
        """Vacía los campos del formulario de registro."""

        for nombre in (
            "id_empleado",
            "nombre_completo",
            "hora_inicio_prevista",
            "hora_fin_prevista",
            "observaciones",
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

    # Panel de Control: estilos, eventos y actualización de indicadores.

    def configurar_panel(self):
        """Conecta los eventos y datos de la segunda pestaña."""
        configurar_estilos_panel(self.ventana)

        self._datos_panel = None
        self.builder.get_object("periodo_grafico").set("Últimos 7 días")
        self.builder.get_object("periodo_grafico").bind(
            "<<ComboboxSelected>>", self.actualizar_panel
        )
        for ident in ("grafico_dias", "grafico_departamentos"):
            self.builder.get_object(ident).bind("<Configure>", self._dibujar_graficos)
        self.actualizar_panel()
        self._actualizar_reloj()

    def _actualizar_reloj(self):
        """Muestra fecha y hora locales sin volver a leer el Excel."""
        ahora = datetime.now()
        dias = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
        meses = ("enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
        fecha = f"{dias[ahora.weekday()].capitalize()}, {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"
        self.builder.get_object("fecha_panel").configure(text=fecha)
        self.builder.get_object("hora_panel").configure(text=ahora.strftime("%H:%M:%S"))
        self.ventana.after(1000, self._actualizar_reloj)

    def actualizar_panel(self, _evento=None):
        """Calcula indicadores y gráficos desde todos los registros del libro."""
        try:
            registros = self.excel.consultar_registros()
        except (ValueError, OSError) as error:
            messagebox.showerror("Panel de Control", str(error), parent=self.ventana)
            return
        periodo = self.builder.get_object("periodo_grafico").get()
        dias = {"Últimos 7 días": 7, "Últimos 14 días": 14,
                "Últimos 30 días": 30}.get(periodo, 7)
        self._datos_panel = build_dashboard_data(registros, dias=dias)
        for campo in ("fichajes_hoy", "entradas_hoy", "salidas_hoy", "jornadas_abiertas"):
            self.builder.get_object(f"valor_{campo}").configure(
                text=str(self._datos_panel[campo])
            )
        self.builder.get_object("actualizado_panel").configure(
            text="Datos actualizados: " + datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        self._dibujar_graficos()

    def _dibujar_graficos(self, _evento=None):
        if self._datos_panel is None:
            return
        dibujar_fichajes_por_dia(
            self.builder.get_object("grafico_dias"), self._datos_panel["dias"]
        )
        dibujar_departamentos(
            self.builder.get_object("grafico_departamentos"),
            self._datos_panel["departamentos"],
        )

    # Methods connecting the interface to Excel

    def guardar_registro(self):
        """Recoge los campos y guarda el registro en Excel."""

        campos = (
            "id_empleado",
            "nombre_completo",
            "departamento",
            "accion",
            "observaciones",
            "hora_inicio_prevista",
            "hora_fin_prevista",
        )

        datos = {
            nombre: self.builder.get_object(nombre).get()
            for nombre in campos
        }

        try:
            self.excel.guardar_registro(**datos)
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo guardar",
                str(error),
                parent=self.ventana,
            )
            return

        self.limpiar_formulario()

        self.builder.get_object("estado_registro").configure(
            text="Registro guardado correctamente"
        )

        self.actualizar_historico()
        self.actualizar_panel()

    def consultar_registros(self):
        """Consulta Excel y actualiza la tabla con los filtros actuales."""

        try:
            registros = self.excel.consultar_registros(
                empleado=self.builder.get_object("buscar_empleado").get(),
                departamento=self.builder.get_object(
                    "filtro_departamento"
                ).get(),
                accion=self.builder.get_object("filtro_accion").get(),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo consultar",
                str(error),
                parent=self.ventana,
            )
            return

        tabla = self.builder.get_object("tabla_fichajes")

        columnas = (
            "id_registro",
            "id_empleado",
            "nombre_completo",
            "departamento",
            "accion",
            "fecha",
            "hora",
            "hora_inicio_prevista",
            "hora_fin_prevista",
            "observaciones",
        )

        # Replace visible rows without deleting the Excel records.
        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)

        for registro in registros:
            tabla.insert(
                "",
                "end",
                values=[
                    registro.get(columna)
                    if registro.get(columna) is not None
                    else ""
                    for columna in columnas
                ],
            )


if __name__ == "__main__":
    ControlHorariosApp().run()
