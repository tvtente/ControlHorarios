"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pygubu

from excel_manager import ExcelManager


UI_FILE = Path(__file__).resolve().parent / "ui" / "control_horarios.ui"


class ControlHorariosApp:
    """Carga el diseño y controla la interfaz gráfica de la aplicación."""

    def __init__(self):
        carpeta_datos = Path(__file__).resolve().parent / "data"
        carpeta_datos.mkdir(parents=True, exist_ok=True)

        self.excel = ExcelManager(
            carpeta_datos / "control_horarios_viajes.xlsx"
        )

        self.ventana = tk.Tk()
        self.ventana.title("Control de horarios")
        self.ventana.geometry("1100x750")
        self.ventana.minsize(900, 600)

        self.configurar_estilos()

        self.builder = pygubu.Builder()
        self.builder.add_from_file(str(UI_FILE))
        self.interfaz = self.builder.get_object("app", self.ventana)
        self.interfaz.pack(fill="both", expand=True)

        self.builder.connect_callbacks(self)
        self.aplicar_estilos_widgets()

        # Apply the primary style to the registration button.
        boton_registrar = self.builder.get_object("registrar_fichaje")
        if boton_registrar is not None:
            boton_registrar.configure(style="Primary.TButton")

        # Apply the secondary style to the clear button.
        boton_limpiar = self.builder.get_object("limpiar_formulario")
        if boton_limpiar is not None:
            boton_limpiar.configure(style="Secondary.TButton")

        # Copy department and action options into the history filters.
        for origen, destino in (
            ("departamento", "filtro_departamento"),
            ("accion", "filtro_accion"),
        ):
            self.builder.get_object(destino).configure(
                values=self.builder.get_object(origen).cget("values")
            )

        self.consultar_registros()

    def configurar_estilos(self):
        """Aplica un diseño visual moderno y uniforme."""

        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")

        fondo = "#F1F5F9"
        blanco = "#FFFFFF"
        texto = "#1E293B"
        azul = "#2563EB"
        azul_hover = "#1D4ED8"
        borde = "#CBD5E1"

        self.ventana.configure(bg=fondo)

        # Main containers
        estilo.configure(
            "TFrame",
            background=fondo,
        )

        # Standard labels
        estilo.configure(
            "TLabel",
            background=fondo,
            foreground=texto,
            font=("Segoe UI", 10),
        )

        # Main title style
        estilo.configure(
            "Title.TLabel",
            background=fondo,
            foreground="#172554",
            font=("Segoe UI", 17, "bold"),
        )

        # Form sections
        estilo.configure(
            "TLabelframe",
            background=blanco,
            bordercolor=borde,
            borderwidth=1,
            relief="solid",
            padding=12,
        )

        estilo.configure(
            "TLabelframe.Label",
            background=blanco,
            foreground="#172554",
            font=("Segoe UI", 10, "bold"),
        )

        # Input fields: white background and darker border settings.
        estilo.configure(
            "TEntry",
            padding=8,
            fieldbackground=blanco,
            foreground="#111111",
            bordercolor="#111111",
            lightcolor="#111111",
            darkcolor="#111111",
            borderwidth=1,
            relief="solid",
        )

        estilo.configure(
            "TCombobox",
            padding=8,
            fieldbackground=blanco,
            foreground="#111111",
            bordercolor="#111111",
            lightcolor="#111111",
            darkcolor="#111111",
            borderwidth=1,
            relief="solid",
        )

        # Standard buttons
        estilo.configure(
            "TButton",
            background=blanco,
            foreground=texto,
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            bordercolor=borde,
            relief="flat",
        )

        estilo.map(
            "TButton",
            background=[
                ("pressed", "#DBEAFE"),
                ("active", "#E2E8F0"),
            ],
            foreground=[
                ("disabled", "#94A3B8"),
                ("active", texto),
            ],
        )

        # Primary action button: stronger color, clear text, and more padding.
        estilo.configure(
            "Primary.TButton",
            background=azul,
            foreground=blanco,
            font=("Segoe UI", 11, "bold"),
            padding=(18, 12),
            borderwidth=0,
            bordercolor=azul,
            relief="flat",
        )

        estilo.map(
            "Primary.TButton",
            background=[
                ("pressed", "#1E40AF"),
                ("active", azul_hover),
            ],
            foreground=[
                ("disabled", "#CBD5E1"),
                ("pressed", blanco),
                ("active", blanco),
                ("!disabled", blanco),
            ],
        )

        # Secondary action button: subtle background and matching spacing.
        estilo.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground="#1E293B",
            font=("Segoe UI", 11, "bold"),
            padding=(18, 12),
            borderwidth=0,
            relief="flat",
        )

        estilo.map(
            "Secondary.TButton",
            background=[
                ("pressed", "#CBD5E1"),
                ("active", "#D1DCEB"),
            ],
            foreground=[
                ("disabled", "#94A3B8"),
                ("!disabled", "#1E293B"),
            ],
        )

        # Tabs
        estilo.configure(
            "TNotebook",
            background=fondo,
            borderwidth=0,
        )

        estilo.configure(
            "TNotebook.Tab",
            background="#E2E8F0",
            foreground=texto,
            font=("Segoe UI", 10, "bold"),
            padding=(18, 11),
        )

        estilo.map(
            "TNotebook.Tab",
            background=[
                ("selected", blanco),
                ("active", "#DBEAFE"),
            ],
            foreground=[
                ("selected", azul),
                ("active", texto),
            ],
        )

        # Excel history table
        estilo.configure(
            "Treeview",
            background=blanco,
            fieldbackground=blanco,
            foreground=texto,
            rowheight=32,
            font=("Segoe UI", 10),
        )

        estilo.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground="#172554",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 10),
        )

        estilo.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", texto)],
        )

    def aplicar_estilos_widgets(self):
        """Mejora la apariencia de los widgets del formulario."""

        estilo = ttk.Style(self.ventana)

        # Labels inside the white employee form
        estilo.configure(
            "Form.TLabel",
            background="#FFFFFF",
            foreground="#111827",
            font=("Segoe UI", 11, "bold"),
        )

        # Main page title
        estilo.configure(
            "PageTitle.TLabel",
            background="#F1F5F9",
            foreground="#172554",
            font=("Segoe UI", 17, "bold"),
        )

        # Apply styles to the existing Pygubu widgets
        label_ids = (
            "etiqueta_id_empleado",
            "etiqueta_nombre",
            "etiqueta_departamento",
            "etiqueta_accion",
            "etiqueta_inicio_previsto",
            "etiqueta_fin_previsto",
            "etiqueta_observaciones",
            "aviso_fecha_hora",
        )

        for widget_id in label_ids:
            widget = self.builder.get_object(widget_id)
            if widget is not None:
                widget.configure(style="Form.TLabel")

        titulo = self.builder.get_object("titulo_registro")
        if titulo is not None:
            titulo.configure(style="PageTitle.TLabel")

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