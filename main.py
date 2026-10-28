"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import pygubu
import ttkbootstrap as tb

from dashboard import build_dashboard_data, dibujar_departamentos, dibujar_fichajes_por_dia
from excel_manager import ExcelManager


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

        self.ventana = tb.Window(themename="cosmo")
        self.ventana.title("Control de horarios")
        self.ventana.geometry("1280x800")
        self.ventana.minsize(1000, 650)

        self.configurar_estilos()

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
        # Connect the history table to its scrollbars.
        tabla = self.builder.get_object("tabla_fichajes")
        scroll_vertical = self.builder.get_object("scroll_vertical")
        scroll_horizontal = self.builder.get_object("scroll_horizontal")

        tabla.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
        )

        scroll_vertical.configure(command=tabla.yview)
        scroll_horizontal.configure(command=tabla.xview)
        self.aplicar_estilos_widgets()

        # Apply the primary style to the registration button.
        boton_registrar = self.builder.get_object("registrar_fichaje")
        if boton_registrar is not None:
            boton_registrar.configure(style="Primary.TButton")

        # Apply the secondary style to the clear button.
        boton_limpiar = self.builder.get_object("limpiar_formulario")
        if boton_limpiar is not None:
            boton_limpiar.configure(style="Secondary.TButton")

        # Load departments from Excel.
        departamentos = self.excel.consultar_departamentos()

        if departamentos:
            self.builder.get_object("departamento").configure(
                values=departamentos
            )

        # Copy department and action options into the history filters.
        for origen, destino in (
            ("departamento", "filtro_departamento"),
            ("accion", "filtro_accion"),
        ):
            self.builder.get_object(destino).configure(
                values=self.builder.get_object(origen).cget("values")
            )

        self._datos_panel = None
        self.builder.get_object("periodo_grafico").set("Últimos 7 días")
        self.builder.get_object("periodo_grafico").bind(
            "<<ComboboxSelected>>", self.actualizar_panel
        )
        for ident in ("grafico_dias", "grafico_departamentos"):
            self.builder.get_object(ident).bind("<Configure>", self._dibujar_graficos)

        self.consultar_registros()
        self.actualizar_panel()
        self._actualizar_reloj()

    def configurar_estilos(self):
        """Aplica un diseño visual moderno y uniforme."""

        estilo = ttk.Style(self.ventana)

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
                ("selected", azul),
                ("active", "#DBEAFE"),
            ],
            foreground=[
                ("selected", blanco),
                ("active", texto),
            ],
        )

        # Panel de control: cabecera, tarjetas y gráficos.
        estilo.configure("PanelHeader.TFrame", background="#EAF3FF")
        estilo.configure("PanelIcon.TLabel", background="#EAF3FF",
                         foreground=azul, font=("Segoe UI", 30, "bold"))
        estilo.configure("PanelTitle.TLabel", background="#EAF3FF",
                         foreground="#0B1F55", font=("Segoe UI", 23, "bold"))
        estilo.configure("PanelSubtitle.TLabel", background="#EAF3FF",
                         foreground="#4C5F7E", font=("Segoe UI", 11))
        estilo.configure("PanelClock.TFrame", background="#DDEBFC")
        estilo.configure("ClockDate.TLabel", background="#DDEBFC",
                         foreground="#0B1F55", font=("Segoe UI", 10, "bold"))
        estilo.configure("ClockTime.TLabel", background="#DDEBFC",
                         foreground="#0B1F55", font=("Segoe UI", 17, "bold"))
        fondos = ("#E9F2FF", "#E7F8EE", "#FFF0F0", "#FFF5DC")
        acentos = ("#1264DC", "#079447", "#D3323C", "#B97800")
        for indice, (color_fondo, color_acento) in enumerate(zip(fondos, acentos)):
            estilo.configure(f"Card{indice}.TFrame", background=color_fondo)
            estilo.configure(f"CardIcon{indice}.TLabel", background=color_fondo,
                             foreground=color_acento, font=("Segoe UI", 25, "bold"))
            estilo.configure(f"CardTitle{indice}.TLabel", background=color_fondo,
                             foreground="#10234E", font=("Segoe UI", 11, "bold"))
            estilo.configure(f"CardValue{indice}.TLabel", background=color_fondo,
                             foreground=color_acento, font=("Segoe UI", 27, "bold"))
            estilo.configure(f"CardSubtitle{indice}.TLabel", background=color_fondo,
                             foreground="#405674", font=("Segoe UI", 9))
        estilo.configure("Chart.TFrame", background=blanco)
        estilo.configure("ChartTitle.TLabel", background=blanco,
                         foreground="#0B1F55", font=("Segoe UI", 14, "bold"))
        estilo.configure("ChartSubtitle.TLabel", background=blanco,
                         foreground="#526687", font=("Segoe UI", 10))
        estilo.configure("PanelNotice.TLabel", background="#E8F2FF",
                         foreground="#1657AC", font=("Segoe UI", 10), padding=10)
        estilo.configure("PanelFooter.TFrame", background="#E9EFF7")
        estilo.configure("PanelFooter.TLabel", background="#E9EFF7",
                         foreground="#243456", font=("Segoe UI", 9))

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
        
        # Modern scrollbars for the Excel history table
        estilo.configure(
            "Vertical.TScrollbar",
            background="#CBD5E1",
            troughcolor="#F1F5F9",
            bordercolor="#F1F5F9",
            arrowcolor="#475569",
            relief="flat",
            width=12,
        )

        estilo.map(
            "Vertical.TScrollbar",
            background=[
                ("active", "#2563EB"),
                ("pressed", "#1D4ED8"),
            ],
        )

        estilo.configure(
            "Horizontal.TScrollbar",
            background="#CBD5E1",
            troughcolor="#F1F5F9",
            bordercolor="#F1F5F9",
            arrowcolor="#475569",
            relief="flat",
            width=12,
        )

        estilo.map(
            "Horizontal.TScrollbar",
            background=[
                ("active", "#2563EB"),
                ("pressed", "#1D4ED8"),
            ],
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

        # Update the number of visible records.
        self.builder.get_object("total_registros").configure(
            text=f"{len(registros)} registros"
        )


if __name__ == "__main__":
    ControlHorariosApp().run()