"""Conecta la interfaz de Pygubu con el gestor de Excel."""

from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import pygubu
import ttkbootstrap as tb

from dashboard import build_dashboard_data, dibujar_departamentos, dibujar_fichajes_por_dia
from excel_manager import ExcelManager
from employee_status import estado_empleado
from styles import TEMA, aplicar_estilos_widgets, configurar_estilos, configurar_estilos_panel


UI_DIR = Path(__file__).resolve().parent / "ui"
UI_FILE = UI_DIR / "control_horarios.ui"
IMAGES_DIR = UI_DIR.parent / "images"


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
        self.ventana.geometry("1280x900")
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

        self._configurar_historico()
        self.configurar_panel()
        self.consultar_registros()
        self.builder.get_object("pie_archivo").configure(
            text=f"Archivo: data/{self.excel.filename.name}"
        )

    # Methods connected to the graphical interface

    def run(self):
        """Inicia el bucle de eventos de la ventana."""
        self.ventana.mainloop()

    def limpiar_formulario(self):
        """Vacía los campos del formulario de registro."""

        for nombre in (
            "id_empleado",
            "nombre_completo",
        ):
            self.builder.get_object(nombre).delete(0, tk.END)

        self.builder.get_object("observaciones").delete("1.0", tk.END)
        self.builder.get_object("departamento").set("")
        self.builder.get_object("accion").set("Entrada a Turno")
        self._restablecer_horas()
        self._actualizar_badge_accion()
        self._empleado_autocompletado = ""
        self._mostrar_estado_empleado({"texto": "Sin fichaje", "color": "#94A3B8"})
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
        hora = ahora.strftime("%H:%M:%S")
        self.builder.get_object("fecha_panel").configure(text=fecha)
        self.builder.get_object("hora_panel").configure(text=hora)
        self.builder.get_object("fecha_registro").configure(text=fecha)
        self.builder.get_object("hora_registro").configure(text=hora)
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

    # Methods connecting the interface to Excel

    def _configurar_registro(self):
        """Conecta el badge visual del tipo de registro sin alterar el guardado."""
        accion = self.builder.get_object("accion")
        accion.set("Entrada a Turno")
        accion.bind("<<ComboboxSelected>>", self._actualizar_badge_accion)
        self._icono_entrada = tk.PhotoImage(file=str(IMAGES_DIR / "entrada.png"))
        self._icono_salida = tk.PhotoImage(file=str(IMAGES_DIR / "salida.png"))
        self._actualizar_badge_accion()
        self._restablecer_horas()
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
            messagebox.showerror("Estado del empleado", str(error), parent=self.ventana)
            return
        estado = estado_empleado(registros, empleado)
        self._mostrar_estado_empleado(estado, empleado)
        perfil = estado["empleado"]
        if completar and not perfil and getattr(self, "_empleado_autocompletado", ""):
            self.builder.get_object("nombre_completo").delete(0, tk.END)
            self.builder.get_object("departamento").set("")
            self._cargar_horario_departamento()
            self._empleado_autocompletado = ""
        if completar and perfil:
            campo_id = self.builder.get_object("id_empleado")
            campo_id.delete(0, tk.END)
            campo_id.insert(0, perfil["id_empleado"])
            self._empleado_autocompletado = empleado
            nombre = self.builder.get_object("nombre_completo")
            nombre.delete(0, tk.END)
            nombre.insert(0, perfil.get("nombre_completo") or "")
            self.builder.get_object("departamento").set(perfil.get("departamento") or "")
            self._cargar_horario_departamento()

    def _cargar_horario_departamento(self, _evento=None):
        """Actualiza los Spinbox con el horario del departamento en Excel."""
        for campo in ("hora_inicio_prevista", "hora_fin_prevista"):
            self.builder.get_object(campo).set("")
        try:
            horario = self.excel.consultar_horario_departamento(
                self.builder.get_object("departamento").get()
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("Horario del departamento", str(error), parent=self.ventana)
            return
        for campo, valor in horario.items():
            self.builder.get_object(campo).set(valor)

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
        for campo, valor in (("hora_inicio_prevista", "08:00"),
                             ("hora_fin_prevista", "17:00")):
            control = self.builder.get_object(campo)
            control.configure(
                values=valores, validate="key",
                validatecommand=(control.register(self._validar_edicion_hora), "%P"),
            )
            control.set(valor)

    def _leer_hora(self, campo):
        valor = self.builder.get_object(campo).get()
        if len(valor) != 5 or not self._validar_edicion_hora(valor):
            etiqueta = "inicio" if campo == "hora_inicio_prevista" else "fin"
            raise ValueError(f"Introduce la hora de {etiqueta} en formato HH:MM (00:00–23:59).")
        return valor

    def _actualizar_badge_accion(self, _evento=None):
        """Colorea el resumen de entrada, salida o descanso según el combobox."""
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
            self.builder.get_object("accion").get(),
            ("AccionNeutro", "●", "TIPO", "Selecciona un registro"),
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

        try:
            datos = {
                nombre: (self._leer_hora(nombre)
                         if nombre in ("hora_inicio_prevista", "hora_fin_prevista")
                         else self.builder.get_object(nombre).get("1.0", "end-1c")
                         if nombre == "observaciones"
                         else self.builder.get_object(nombre).get())
                for nombre in campos
            }
            self.excel.guardar_registro(**datos)
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "No se pudo guardar",
                str(error),
                parent=self.ventana,
            )
            return

        self.limpiar_formulario()

        self._actualizar_estado_empleado(empleado=datos["id_empleado"], completar=False)

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

        # Los últimos fichajes aparecen primero. Los filtros reinician la página.
        self._registros_historico = list(reversed(registros))
        self._pagina_historico = 0
        self._mostrar_pagina_historico()

    def _configurar_historico(self):
        self._registros_historico = []
        self._pagina_historico = 0
        self._registros_por_pagina = 20
        tabla = self.builder.get_object("tabla_fichajes")
        vertical = self.builder.get_object("scroll_vertical")
        horizontal = self.builder.get_object("scroll_horizontal")
        tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.configure(command=tabla.yview)
        horizontal.configure(command=tabla.xview)

    def pagina_anterior(self):
        if self._pagina_historico > 0:
            self._pagina_historico -= 1
            self._mostrar_pagina_historico()

    def pagina_siguiente(self):
        if (self._pagina_historico + 1) * self._registros_por_pagina < len(self._registros_historico):
            self._pagina_historico += 1
            self._mostrar_pagina_historico()

    def _mostrar_pagina_historico(self):
        tabla = self.builder.get_object("tabla_fichajes")
        total = len(self._registros_historico)
        paginas = max(1, (total + self._registros_por_pagina - 1) // self._registros_por_pagina)
        self._pagina_historico = min(self._pagina_historico, paginas - 1)
        inicio = self._pagina_historico * self._registros_por_pagina
        fin = min(inicio + self._registros_por_pagina, total)
        columnas = (
            "id_registro", "id_empleado", "nombre_completo", "departamento",
            "accion", "fecha", "hora", "hora_inicio_prevista",
            "hora_fin_prevista", "observaciones",
        )
        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)
        for registro in self._registros_historico[inicio:fin]:
            tabla.insert("", "end", values=[
                registro.get(c) if registro.get(c) is not None else "" for c in columnas
            ])
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
        self.builder.get_object("pagina_siguiente").configure(
            state="normal" if fin < total else "disabled"
        )


if __name__ == "__main__":
    ControlHorariosApp().run()
