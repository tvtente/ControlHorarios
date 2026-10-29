"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, ttk

import pygubu
import ttkbootstrap as tb
from ttkbootstrap.dialogs import DatePickerDialog

from dashboard import build_dashboard_data, dibujar_departamentos, dibujar_fichajes_por_dia
from excel_manager import ExcelManager
from employee_status import (
    estado_empleado, filtrar_fichajes_por_fecha, interpretar_rango_fechas,
    ordenar_fichajes, siguiente_fichaje,
)
from styles import TEMA, aplicar_estilos_widgets, configurar_estilos, configurar_estilos_panel


def texto_error(error):
    """Presenta en español los problemas habituales de acceso al archivo."""
    if isinstance(error, PermissionError):
        return "No se puede acceder al Excel. Ciérralo si está abierto y comprueba los permisos del archivo."
    if isinstance(error, FileNotFoundError):
        return "No se encuentra el archivo de fichajes. Comprueba que exista en la carpeta data."
    if isinstance(error, OSError):
        return "No se ha podido acceder al archivo de fichajes. Comprueba su ubicación y los permisos."
    return str(error)


UI_DIR = Path(__file__).resolve().parent / "ui"
UI_FILE = UI_DIR / "control_horarios.ui"
IMAGES_DIR = UI_DIR.parent / "images"
CAMPOS_HORARIO = (
    "hora_inicio_prevista",
    "hora_fin_prevista",
    "hora_inicio_descanso_prevista",
    "hora_fin_descanso_prevista",
)
ACCION_POR_CAMPO = dict(zip(CAMPOS_HORARIO, (
    "Entrada a Turno",
    "Salida de Turno",
    "Inicio de Descanso",
    "Fin de Descanso",
)))
ACCIONES_HISTORICO = {
    "accion_entrada": "Entrada a Turno",
    "accion_inicio_descanso": "Inicio de Descanso",
    "accion_fin_descanso": "Fin de Descanso",
    "accion_salida": "Salida de Turno",
}
COLUMNAS_HISTORICO = (
    "id_registro", "id_empleado", "nombre_completo", "departamento",
    "accion", "fecha", "hora", "hora_inicio_prevista",
    "hora_fin_prevista", "hora_inicio_descanso_prevista",
    "hora_fin_descanso_prevista", "horas_trabajadas",
    "cumplimiento", "observaciones",
)
COLORES_CUMPLIMIENTO = {
    "A tiempo": "#006100",
    "Cumple horario": "#006100",
    "Tarde": "#9C0006",
    "Salida anticipada": "#9C6500",
    "No aplica": "#44546A",
}


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
            carpeta_datos / "control_horarios.xlsx"
        )

        self.ventana = tb.Window(themename=TEMA)
        self.ventana.title("Control de horarios")
        self._icono_ventana = tk.PhotoImage(file=str(IMAGES_DIR / "control_horarios.png"))
        self.ventana.iconphoto(True, self._icono_ventana)
        self.ventana.geometry("1280x980")
        self.ventana.minsize(1000, 850)

        configurar_estilos(self.ventana)

        general = pygubu.Builder()
        general.add_resource_path(IMAGES_DIR)
        general.add_from_file(str(UI_FILE))
        self.interfaz = general.get_object("app", self.ventana)
        self.interfaz.pack(fill="both", expand=True)

        constructores = [general]
        for nombre in ("registro", "panel", "historico"):
            constructor = pygubu.Builder()
            constructor.add_resource_path(IMAGES_DIR)
            constructor.add_from_file(str(UI_DIR / f"{nombre}.ui"))
            contenedor = general.get_object(f"contenedor_{nombre}")
            pantalla = constructor.get_object(f"pantalla_{nombre}", contenedor)
            pantalla.pack(fill="both", expand=True)
            constructores.append(constructor)

        self.builder = ConstructoresPygubu(constructores)

        self.builder.connect_callbacks(self)
        aplicar_estilos_widgets(self.ventana, self.builder)
        self._configurar_registro()

        # Carga los departamentos desde Excel.
        departamentos = self.excel.consultar_departamentos()

        self.builder.get_object("departamento").configure(values=departamentos)

        # Copia las opciones de departamento y acción a los filtros del histórico.
        self.builder.get_object("filtro_departamento").configure(
            values=self.builder.get_object("departamento").cget("values")
        )

        self._configurar_historico()
        self.configurar_panel()
        self.consultar_registros()
        self.builder.get_object("pie_archivo").configure(
            text=f"Archivo: data/{self.excel.filename.name}"
        )
        self.builder.get_object("pestanas").bind(
            "<<NotebookTabChanged>>", self._al_cambiar_pestana
        )

    # Acciones de la interfaz gráfica.

    def _al_cambiar_pestana(self, evento):
        """Recarga la vista seleccionada con los datos actuales del Excel."""
        pestanas = self.builder.get_object("pestanas")
        if evento.widget != pestanas:
            return
        indice = pestanas.index(pestanas.select())
        if indice == 0:
            try:
                departamentos = self.excel.consultar_departamentos()
            except (ValueError, OSError) as error:
                messagebox.showerror("Departamentos", texto_error(error), parent=self.ventana)
                return
            for campo in ("departamento", "filtro_departamento"):
                self.builder.get_object(campo).configure(values=departamentos)
            self._actualizar_estado_empleado(completar=False)
        elif indice == 1:
            self.actualizar_panel()
        elif indice == 2:
            self.consultar_registros()

    def run(self):
        """Inicia el bucle de eventos de la ventana."""
        self.ventana.mainloop()

    def limpiar_formulario(self):
        """Vacía los campos del formulario de registro."""

        self.builder.get_object("nombre_completo").state(["!readonly"])
        for nombre in (
            "id_empleado",
            "nombre_completo",
        ):
            self.builder.get_object(nombre).delete(0, tk.END)

        self.builder.get_object("observaciones").delete("1.0", tk.END)
        self.builder.get_object("departamento").set("")
        self._accion = ""
        self._restablecer_horas()
        self._activar_campo_horario(None)
        self._actualizar_badge_accion()
        for nombre in ("id_empleado", "nombre_completo", "departamento",
                       *CAMPOS_HORARIO):
            self.builder.get_object(nombre).state(["!invalid"])
        self._empleado_autocompletado = ""
        self._mostrar_estado_empleado({"texto": "Sin fichaje", "color": "#94A3B8"})
        self.builder.get_object("id_empleado").focus_set()

    def limpiar_filtros(self):
        """Restablece los filtros y vuelve a mostrar todos los registros."""

        self.builder.get_object("buscar_empleado").delete(0, tk.END)

        self.builder.get_object("filtro_departamento").set("")
        for nombre in ("fecha_desde", "fecha_hasta"):
            campo = self.builder.get_object(nombre)
            campo.delete(0, tk.END)
            campo.state(["!invalid"])
        self._seleccionar_todas_acciones()

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
        fecha_anterior = getattr(self, "_fecha_reloj", ahora.date())
        self._fecha_reloj = ahora.date()
        dias = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
        meses = ("enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
        fecha = f"{dias[ahora.weekday()].capitalize()}, {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"
        hora = ahora.strftime("%H:%M:%S")
        self.builder.get_object("fecha_panel").configure(text=fecha)
        self.builder.get_object("hora_panel").configure(text=hora)
        self.builder.get_object("fecha_registro").configure(text=fecha)
        self.builder.get_object("hora_registro").configure(text=hora)
        if fecha_anterior != ahora.date():
            self._actualizar_estado_empleado(completar=False)
            self.actualizar_panel()
        self.ventana.after(1000, self._actualizar_reloj)

    def actualizar_panel(self, _evento=None):
        """Calcula indicadores y gráficos desde todos los registros del libro."""
        try:
            registros = self.excel.consultar_registros()
        except (ValueError, OSError) as error:
            messagebox.showerror("Panel de Control", texto_error(error), parent=self.ventana)
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
        self.builder.get_object("pie_registros_hoy").configure(
            text=f"{self._datos_panel['fichajes_hoy']} registros hoy"
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

    # Conexión de la interfaz con Excel.

    def _configurar_registro(self):
        """Prepara los controles del flujo de fichaje."""
        self._accion = ""
        for campo in CAMPOS_HORARIO:
            boton = self.builder.get_object(campo.replace("hora_", "boton_"))
            boton.configure(
                command=lambda nombre=campo: self._seleccionar_horario(nombre)
            )
        self._icono_entrada = tk.PhotoImage(file=str(IMAGES_DIR / "entrada.png"))
        self._icono_salida = tk.PhotoImage(file=str(IMAGES_DIR / "salida.png"))
        self._actualizar_badge_accion()
        self._restablecer_horas()
        self._activar_campo_horario(None)
        self.builder.get_object("departamento").bind(
            "<<ComboboxSelected>>", self._cargar_horario_departamento
        )
        self._configurar_ayuda_id()
        self.builder.get_object("id_empleado").bind("<FocusOut>", self._actualizar_estado_empleado)
        self.builder.get_object("id_empleado").bind("<Return>", self._actualizar_estado_empleado)


    def _configurar_ayuda_id(self):
        """Superpone la sugerencia sin introducirla en el valor del campo."""
        campo = self.builder.get_object("id_empleado")
        self._valor_id = tk.StringVar(master=self.ventana, value=campo.get())
        campo.configure(textvariable=self._valor_id)
        estilo = ttk.Style(self.ventana)
        estilo.configure("AyudaID.TLabel", background="#FFFFFF", foreground="#94A3B8")
        self._ayuda_id = ttk.Label(campo, text="EMP-000", style="AyudaID.TLabel",
                                  font=campo.cget("font"), takefocus=False)
        self._ayuda_id.bind("<Button-1>", lambda _evento: campo.focus_set())
        def actualizar(*_args):
            if self._valor_id.get():
                self._ayuda_id.place_forget()
            else:
                self._ayuda_id.place(x=12, rely=0.5, anchor="w")
        self._valor_id.trace_add("write", actualizar)
        actualizar()

    def _mostrar_estado_empleado(self, estado, empleado=""):
        estilo = ttk.Style(self.ventana)
        estilo.configure("RegistroStatusDot.TLabel", foreground=estado["color"])
        self.builder.get_object("estado_registro").configure(text=estado["texto"])
        self.builder.get_object("estado_actual_titulo").configure(
            text=f"Estado · {empleado}" if empleado else "Estado actual"
        )

    def _actualizar_estado_empleado(self, _evento=None, *, empleado=None, completar=True):
        """Consulta al abandonar el ID y completa los datos del empleado conocido."""
        empleado = empleado if empleado is not None else self.builder.get_object("id_empleado").get().strip()
        try:
            registros = self.excel.consultar_registros() if empleado else []
        except (ValueError, OSError) as error:
            self._mostrar_estado_empleado({"texto": "No disponible", "color": "#D3323C"}, empleado)
            self._accion = ""
            self._activar_campo_horario(None)
            self._actualizar_badge_accion()
            messagebox.showerror("Estado del empleado", texto_error(error), parent=self.ventana)
            return
        estado = estado_empleado(registros, empleado)
        self._mostrar_estado_empleado(estado, empleado)
        perfil = estado["empleado"]
        nombre = self.builder.get_object("nombre_completo")
        nombre.state(["!readonly"])
        if completar and not perfil and getattr(self, "_empleado_autocompletado", ""):
            nombre.delete(0, tk.END)
            self.builder.get_object("departamento").set("")
            self._cargar_horario_departamento()
            self._empleado_autocompletado = ""
        if completar and perfil:
            campo_id = self.builder.get_object("id_empleado")
            campo_id.delete(0, tk.END)
            campo_id.insert(0, perfil["id_empleado"])
            self._empleado_autocompletado = empleado
            nombre.delete(0, tk.END)
            nombre.insert(0, perfil.get("nombre_completo") or "")
            self.builder.get_object("departamento").set(perfil.get("departamento") or "")
            self._cargar_horario_departamento()
        if perfil:
            nombre.state(["readonly"])
        self._actualizar_flujo(registros, empleado)

    def _actualizar_flujo(self, registros, empleado):
        """Activa únicamente la etapa pendiente de la jornada del empleado."""
        siguiente = siguiente_fichaje(registros, empleado) if empleado else None
        self._accion = siguiente or ""
        campo = next(
            (nombre for nombre, accion in ACCION_POR_CAMPO.items() if accion == siguiente),
            None,
        )
        self._activar_campo_horario(campo)
        self._actualizar_badge_accion()

    def _cargar_horario_departamento(self, _evento=None):
        """Actualiza los Spinbox con el horario del departamento en Excel."""
        try:
            for campo in CAMPOS_HORARIO:
                self.builder.get_object(campo).set("")
            horario = self.excel.consultar_horario_departamento(
                self.builder.get_object("departamento").get()
            )
            for campo, valor in horario.items():
                self.builder.get_object(campo).set(valor)
        except (ValueError, OSError) as error:
            messagebox.showerror("Horario del departamento", texto_error(error), parent=self.ventana)

    def _activar_campo_horario(self, campo_activo):
        """Habilita solo el siguiente movimiento permitido."""
        for campo in CAMPOS_HORARIO:
            disponible = campo == campo_activo
            self.builder.get_object(campo).state(
                ["!disabled"] if disponible else ["disabled"]
            )
            self.builder.get_object(campo.replace("hora_", "boton_")).state(
                ["!disabled"] if disponible else ["disabled"]
            )
        self.builder.get_object("registrar_fichaje").state(
            ["!disabled"] if campo_activo else ["disabled"]
        )

    def _seleccionar_horario(self, campo):
        """Registra el movimiento del único botón habilitado."""
        if ACCION_POR_CAMPO[campo] != self._accion:
            return
        self.guardar_registro()

    @staticmethod
    def _validar_edicion_hora(valor):
        """Permite editar HH:MM sin admitir letras ni horas fuera de rango."""
        if len(valor) > 5:
            return False
        for indice, caracter in enumerate(valor):
            if indice == 2:
                if caracter != ":":
                    return False
            elif caracter not in "0123456789":
                return False
        if len(valor) >= 2 and int(valor[:2]) > 23:
            return False
        if len(valor) >= 4 and int(valor[3]) > 5:
            return False
        return True

    def _restablecer_horas(self):
        """Configura un Spinbox HH:MM por campo, con pasos de un minuto."""
        valores = tuple(f"{h:02d}:{m:02d}" for h in range(24) for m in range(60))
        anterior = getattr(self, "_cargando_horarios", False)
        self._cargando_horarios = True
        try:
            for campo in CAMPOS_HORARIO:
                control = self.builder.get_object(campo)
                control.configure(
                    values=valores, validate="key",
                    validatecommand=(control.register(self._validar_edicion_hora), "%P"),
                )
                control.set("")
        finally:
            self._cargando_horarios = anterior

    def _leer_hora(self, campo, *, opcional=False):
        valor = self.builder.get_object(campo).get()
        if opcional and not valor:
            return ""
        if len(valor) != 5 or not self._validar_edicion_hora(valor):
            self._marcar_campo_invalido(campo)
            etiqueta = "inicio" if "inicio" in campo else "fin"
            raise ValueError(f"Introduce la hora de {etiqueta} en formato HH:MM (00:00–23:59).")
        return valor

    def _actualizar_badge_accion(self, _evento=None):
        """Colorea el siguiente movimiento permitido."""
        estilos = {
            "Entrada a Turno": (
                "AccionEntrada", "➜", "ENTRADA", "Inicio de jornada"
            ),
            "Salida de Turno": (
                "AccionSalida", "⇦", "SALIDA", "Fin de jornada"
            ),
            "Inicio de Descanso": (
                "AccionDescanso", "⏸", "DESCANSO", "Inicio de pausa"
            ),
            "Fin de Descanso": (
                "AccionDescanso", "▶", "DESCANSO", "Fin de pausa"
            ),
        }
        prefijo, icono, titulo, subtitulo = estilos.get(
            self._accion,
            ("AccionNeutro", "●", "SIN MOVIMIENTO", "Introduce un ID o espera al próximo día"),
        )
        self.builder.get_object("badge_accion").configure(style=f"{prefijo}.TFrame")
        imagen = {"AccionEntrada": self._icono_entrada,
                  "AccionSalida": self._icono_salida}.get(prefijo, "")
        self.builder.get_object("icono_badge_accion").configure(
            style=f"{prefijo}Icon.TLabel", image=imagen,
            text="" if imagen else icono
        )
        self.builder.get_object("titulo_badge_accion").configure(
            style=f"{prefijo}Title.TLabel", text=titulo
        )
        self.builder.get_object("subtitulo_badge_accion").configure(
            style=f"{prefijo}Sub.TLabel", text=subtitulo
        )

    def _marcar_campo_invalido(self, nombre):
        campo = self.builder.get_object(nombre)
        campo.state(["invalid"])
        campo.focus_set()

    def _validar_campos_obligatorios(self):
        """Indica el primer campo pendiente antes de comprobar el horario."""
        campos = (
            ("id_empleado", "Introduce el ID del empleado (por ejemplo, EMP-001)."),
            ("nombre_completo", "Introduce el nombre completo del empleado."),
            ("departamento", "Selecciona el departamento del empleado."),
        )
        for nombre in (*[c[0] for c in campos], *CAMPOS_HORARIO):
            self.builder.get_object(nombre).state(["!invalid"])
        for nombre, mensaje in campos:
            if not self.builder.get_object(nombre).get().strip():
                self._marcar_campo_invalido(nombre)
                raise ValueError(mensaje)
        if not self._accion:
            raise ValueError("No hay un movimiento disponible para este empleado ahora.")

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
            "hora_inicio_descanso_prevista",
            "hora_fin_descanso_prevista",
        )

        try:
            self._validar_campos_obligatorios()
            datos = {
                nombre: (self._leer_hora(
                            nombre,
                            opcional=nombre in (
                                "hora_inicio_descanso_prevista",
                                "hora_fin_descanso_prevista",
                            ),
                         )
                         if nombre in CAMPOS_HORARIO
                         else self.builder.get_object(nombre).get("1.0", "end-1c")
                         if nombre == "observaciones"
                         else self._accion if nombre == "accion"
                         else self.builder.get_object(nombre).get())
                for nombre in campos
            }
            self.excel.guardar_registro(**datos)
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo guardar",
                texto_error(error),
                parent=self.ventana,
            )
            return

        self.builder.get_object("observaciones").delete("1.0", tk.END)
        self._actualizar_estado_empleado(empleado=datos["id_empleado"], completar=False)

        self.actualizar_historico()
        self.actualizar_panel()

    def consultar_registros(self):
        """Consulta Excel y actualiza la tabla con los filtros actuales."""

        try:
            for nombre in ("fecha_desde", "fecha_hasta"):
                self.builder.get_object(nombre).state(["!invalid"])
            desde, hasta = interpretar_rango_fechas(
                self.builder.get_object("fecha_desde").get(),
                self.builder.get_object("fecha_hasta").get(),
            )
            registros = self.excel.consultar_registros(
                empleado=self.builder.get_object("buscar_empleado").get(),
                departamento=self.builder.get_object(
                    "filtro_departamento"
                ).get(),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo consultar",
                texto_error(error),
                parent=self.ventana,
            )
            return

        registros = filtrar_fichajes_por_fecha(registros, desde, hasta)

        if not self._filtro_todos.get():
            seleccionadas = {
                accion for nombre, accion in ACCIONES_HISTORICO.items()
                if self._filtros_accion[nombre].get()
            }
            registros = [r for r in registros if r.get("accion") in seleccionadas]

        # Conserva la columna elegida y ordena antes de paginar.
        self._registros_historico = ordenar_fichajes(
            registros, self._columna_orden, self._orden_descendente
        )
        self._pagina_historico = 0
        self._mostrar_pagina_historico()

    def _elegir_fecha_historico(self, nombre):
        campo = self.builder.get_object(nombre)
        try:
            inicio = datetime.strptime(campo.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            inicio = date.today()
        dialogo = DatePickerDialog(parent=self.ventana, start_date=inicio, first_weekday=0)
        if dialogo.date_selected:
            campo.delete(0, tk.END)
            campo.insert(0, dialogo.date_selected.strftime("%d/%m/%Y"))
            campo.state(["!invalid"])

    def elegir_fecha_desde(self):
        self._elegir_fecha_historico("fecha_desde")

    def elegir_fecha_hasta(self):
        self._elegir_fecha_historico("fecha_hasta")

    def _configurar_historico(self):
        self._filtro_todos = tk.BooleanVar(master=self.ventana, value=True)
        self.builder.get_object("accion_todos").configure(
            variable=self._filtro_todos, command=self._seleccionar_todas_acciones
        )
        self._filtros_accion = {}
        for nombre in ACCIONES_HISTORICO:
            variable = tk.BooleanVar(master=self.ventana, value=False)
            self._filtros_accion[nombre] = variable
            self.builder.get_object(nombre).configure(
                variable=variable, command=self._seleccionar_accion
            )
        self._registros_historico = []
        self._pagina_historico = 0
        self._registros_por_pagina = 20
        self._columna_orden = "fecha"
        self._orden_descendente = True
        tabla = self.builder.get_object("tabla_fichajes")
        for estado, color in COLORES_CUMPLIMIENTO.items():
            tabla.tag_configure(estado, foreground=color)
        self._titulos_columnas = {}
        for columna_ui, campo in zip(tabla["columns"], COLUMNAS_HISTORICO):
            titulo = tabla.heading(columna_ui, "text")
            self._titulos_columnas[campo] = (columna_ui, titulo)
            tabla.heading(columna_ui, command=lambda nombre=campo: self.ordenar_historico(nombre))
        self._mostrar_orden_historico()
        vertical = self.builder.get_object("scroll_vertical")
        horizontal = self.builder.get_object("scroll_horizontal")
        tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.configure(command=tabla.yview)
        horizontal.configure(command=tabla.xview)

    def ordenar_historico(self, columna):
        """Alterna ascendente/descendente al pulsar un encabezado."""
        if columna == self._columna_orden:
            self._orden_descendente = not self._orden_descendente
        else:
            self._columna_orden = columna
            self._orden_descendente = False
        self._registros_historico = ordenar_fichajes(
            self._registros_historico, self._columna_orden, self._orden_descendente
        )
        self._pagina_historico = 0
        self._mostrar_orden_historico()
        self._mostrar_pagina_historico()

    def _mostrar_orden_historico(self):
        tabla = self.builder.get_object("tabla_fichajes")
        for campo, (columna_ui, titulo) in self._titulos_columnas.items():
            flecha = " ↓" if self._orden_descendente else " ↑"
            tabla.heading(columna_ui, text=titulo + flecha if campo == self._columna_orden else titulo)

    def _seleccionar_todas_acciones(self):
        """Todos muestra las cuatro acciones; las casillas individuales filtran."""
        self._filtro_todos.set(True)
        for variable in self._filtros_accion.values():
            variable.set(False)

    def _seleccionar_accion(self):
        self._filtro_todos.set(False)
        if not any(variable.get() for variable in self._filtros_accion.values()):
            self._seleccionar_todas_acciones()

    def pagina_anterior(self):
        if self._pagina_historico > 0:
            self._pagina_historico -= 1
            self._mostrar_pagina_historico()

    def pagina_inicio(self):
        """Vuelve a la primera página del histórico filtrado."""
        self._pagina_historico = 0
        self._mostrar_pagina_historico()

    def pagina_siguiente(self):
        if (self._pagina_historico + 1) * self._registros_por_pagina < len(self._registros_historico):
            self._pagina_historico += 1
            self._mostrar_pagina_historico()

    def pagina_final(self):
        """Salta a la última página del histórico filtrado."""
        total = len(self._registros_historico)
        self._pagina_historico = max(0, (total - 1) // self._registros_por_pagina)
        self._mostrar_pagina_historico()

    def _mostrar_pagina_historico(self):
        tabla = self.builder.get_object("tabla_fichajes")
        total = len(self._registros_historico)
        paginas = max(1, (total + self._registros_por_pagina - 1) // self._registros_por_pagina)
        self._pagina_historico = min(self._pagina_historico, paginas - 1)
        inicio = self._pagina_historico * self._registros_por_pagina
        fin = min(inicio + self._registros_por_pagina, total)
        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)
        for registro in self._registros_historico[inicio:fin]:
            estado = registro.get("cumplimiento") or ""
            valores = [
                registro.get(c) if registro.get(c) is not None else ""
                for c in COLUMNAS_HISTORICO
            ]
            if estado:
                valores[-2] = "● " + estado
            tabla.insert("", "end", values=valores,
                         tags=(estado,) if estado in COLORES_CUMPLIMIENTO else ())
        tabla.yview_moveto(0)
        self.builder.get_object("total_registros").configure(
            text=f"{inicio + 1 if total else 0}–{fin} de {total} registros"
        )
        self.builder.get_object("indicador_pagina").configure(
            text=f"Página {self._pagina_historico + 1} de {paginas}"
        )
        self.builder.get_object("pagina_anterior").configure(
            state="normal" if self._pagina_historico > 0 else "disabled"
        )
        self.builder.get_object("pagina_inicio").configure(
            state="normal" if self._pagina_historico > 0 else "disabled"
        )
        self.builder.get_object("pagina_siguiente").configure(
            state="normal" if fin < total else "disabled"
        )
        self.builder.get_object("pagina_final").configure(
            state="normal" if fin < total else "disabled"
        )


if __name__ == "__main__":
    ControlHorariosApp().run()
