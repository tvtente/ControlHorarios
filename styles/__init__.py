"""Estilos ttk compartidos por las tres interfaces Pygubu."""

from tkinter import TclError, font as tkfont, ttk

TEMA = "cosmo"

# Prefer rounded, antialiased families so digits are not bitmap-pixelated.
PREFERENCIA_FUENTE = (
    "Ubuntu Sans",
    "Ubuntu",
    "Noto Sans",
    "DejaVu Sans",
    "Liberation Sans",
    "Segoe UI",
    "Helvetica",
    "Arial",
)

FUENTE = "Noto Sans"


def tipo(tamano, *peso):
    """Fuente TrueType redondeada para etiquetas, botones y números."""
    if peso:
        return (FUENTE, tamano) + peso
    return (FUENTE, tamano)


def _elegir_fuente(ventana):
    """Elige la primera familia instalada de la lista de preferencia."""
    global FUENTE
    disponibles = {nombre.casefold() for nombre in tkfont.families(ventana)}
    for nombre in PREFERENCIA_FUENTE:
        if nombre.casefold() in disponibles:
            FUENTE = nombre
            break
    for nombre_tk in (
        "TkDefaultFont",
        "TkTextFont",
        "TkHeadingFont",
        "TkMenuFont",
        "TkCaptionFont",
    ):
        try:
            tkfont.nametofont(nombre_tk).configure(family=FUENTE)
        except TclError:
            pass
    return FUENTE


def configurar_estilos(ventana):
    """Aplica un diseño visual moderno y uniforme."""

    _elegir_fuente(ventana)
    estilo = ttk.Style(ventana)

    fondo = "#F1F5F9"
    blanco = "#FFFFFF"
    texto = "#1E293B"
    azul = "#2563EB"
    azul_hover = "#1D4ED8"
    borde = "#CBD5E1"

    ventana.configure(bg=fondo)

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
        font=tipo(10),
    )

    # Main title style
    estilo.configure(
        "Title.TLabel",
        background=fondo,
        foreground="#172554",
        font=tipo(17, "bold"),
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
        font=tipo(10, "bold"),
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
        font=tipo(10, "bold"),
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
        font=tipo(11, "bold"),
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
        font=tipo(11, "bold"),
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
        font=tipo(10, "bold"),
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

    # Excel history table
    estilo.configure(
        "Treeview",
        background=blanco,
        fieldbackground=blanco,
        foreground=texto,
        rowheight=32,
        font=tipo(10),
    )

    estilo.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground="#172554",
        font=tipo(10, "bold"),
        padding=(8, 10),
    )

    estilo.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", texto)],
    )

def aplicar_estilos_widgets(ventana, builder):
    """Mejora la apariencia de los widgets del formulario."""

    estilo = ttk.Style(ventana)

    # Labels inside the white employee form
    estilo.configure(
        "Form.TLabel",
        background="#FFFFFF",
        foreground="#111827",
        font=tipo(11, "bold"),
    )

    # Main page title
    estilo.configure(
        "PageTitle.TLabel",
        background="#F1F5F9",
        foreground="#172554",
        font=tipo(17, "bold"),
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
        widget = builder.get_object(widget_id)
        if widget is not None:
            widget.configure(style="Form.TLabel")

    titulo = builder.get_object("titulo_registro")
    if titulo is not None:
        titulo.configure(style="PageTitle.TLabel")

    boton_registrar = builder.get_object("registrar_fichaje")
    if boton_registrar is not None:
        boton_registrar.configure(style="Primary.TButton")

    boton_limpiar = builder.get_object("limpiar_formulario")
    if boton_limpiar is not None:
        boton_limpiar.configure(style="Secondary.TButton")


def configurar_estilos_panel(ventana):
    """Define los estilos exclusivos del Panel de Control."""
    _elegir_fuente(ventana)
    estilo = ttk.Style(ventana)
    azul = "#2563EB"
    blanco = "#FFFFFF"

    estilo.configure("PanelHeader.TFrame", background="#EAF3FF")
    estilo.configure("PanelIcon.TLabel", background="#EAF3FF",
                     foreground=azul, font=tipo(30, "bold"))
    estilo.configure("PanelTitle.TLabel", background="#EAF3FF",
                     foreground="#0B1F55", font=tipo(23, "bold"))
    estilo.configure("PanelSubtitle.TLabel", background="#EAF3FF",
                     foreground="#4C5F7E", font=tipo(11))
    estilo.configure("PanelClock.TFrame", background="#DDEBFC")
    estilo.configure("ClockDate.TLabel", background="#DDEBFC",
                     foreground="#0B1F55", font=tipo(10, "bold"))
    estilo.configure("ClockTime.TLabel", background="#DDEBFC",
                     foreground="#0B1F55", font=tipo(17, "bold"))
    fondos = ("#E9F2FF", "#E7F8EE", "#FFF0F0", "#FFF5DC")
    acentos = ("#1264DC", "#079447", "#D3323C", "#B97800")
    for indice, (color_fondo, color_acento) in enumerate(zip(fondos, acentos)):
        estilo.configure(f"Card{indice}.TFrame", background=color_fondo)
        estilo.configure(f"CardIcon{indice}.TLabel", background=color_fondo,
                         foreground=color_acento, font=tipo(25, "bold"))
        estilo.configure(f"CardTitle{indice}.TLabel", background=color_fondo,
                         foreground="#10234E", font=tipo(11, "bold"))
        estilo.configure(f"CardValue{indice}.TLabel", background=color_fondo,
                         foreground=color_acento, font=tipo(28, "bold"))
        estilo.configure(f"CardSubtitle{indice}.TLabel", background=color_fondo,
                         foreground="#405674", font=tipo(9))
    estilo.configure("Chart.TFrame", background=blanco)
    estilo.configure("ChartTitle.TLabel", background=blanco,
                     foreground="#0B1F55", font=tipo(14, "bold"))
    estilo.configure("ChartSubtitle.TLabel", background=blanco,
                     foreground="#526687", font=tipo(10))
    estilo.configure("PanelNotice.TLabel", background="#E8F2FF",
                     foreground="#1657AC", font=tipo(10), padding=10)
    estilo.configure("PanelFooter.TFrame", background="#E9EFF7")
    estilo.configure("PanelFooter.TLabel", background="#E9EFF7",
                     foreground="#243456", font=tipo(9))

