"""Estilos ttk compartidos por las tres interfaces Pygubu."""

from tkinter import TclError, font as tkfont, ttk

TEMA = "cosmo"

# Prefer rounded, antialiased families so digits are not bitmap-pixelated.
PREFERENCIA_FUENTE = (
    "Noto Sans",
    "DejaVu Sans",
    "Ubuntu",
    "Ubuntu Sans",
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

    # Registration screen cards (Fichaje / Registro)
    estilo.configure("RegistroHeader.TFrame", background="#EAF3FF")
    estilo.configure(
        "RegistroIcon.TLabel",
        background="#EAF3FF",
        foreground=azul,
        font=tipo(28, "bold"),
    )
    estilo.configure(
        "RegistroTitle.TLabel",
        background="#EAF3FF",
        foreground="#0B1F55",
        font=tipo(20, "bold"),
    )
    estilo.configure(
        "RegistroSubtitle.TLabel",
        background="#EAF3FF",
        foreground="#4C5F7E",
        font=tipo(10),
    )
    estilo.configure("RegistroClock.TFrame", background="#DDEBFC")
    estilo.configure(
        "RegistroClockIcon.TLabel",
        background="#DDEBFC",
        foreground=azul,
        font=tipo(18, "bold"),
    )
    estilo.configure(
        "RegistroClockDate.TLabel",
        background="#DDEBFC",
        foreground="#0B1F55",
        font=tipo(9, "bold"),
    )
    estilo.configure(
        "RegistroClockTime.TLabel",
        background="#DDEBFC",
        foreground="#0B1F55",
        font=tipo(16, "bold"),
    )
    estilo.configure("RegistroStatus.TFrame", background=blanco)
    estilo.configure(
        "RegistroStatusDot.TLabel",
        background=blanco,
        foreground="#94A3B8",
        font=tipo(12),
    )
    estilo.configure(
        "RegistroStatusCaption.TLabel",
        background=blanco,
        foreground="#64748B",
        font=tipo(8),
    )
    estilo.configure(
        "RegistroStatusValue.TLabel",
        background=blanco,
        foreground="#0F172A",
        font=tipo(10, "bold"),
    )
    estilo.configure("RegistroCard.TFrame", background=blanco)
    estilo.configure(
        "RegistroCardIcon.TLabel",
        background=blanco,
        foreground=azul,
        font=tipo(16, "bold"),
    )
    estilo.configure(
        "RegistroCardTitle.TLabel",
        background=blanco,
        foreground="#0B1F55",
        font=tipo(12, "bold"),
    )
    estilo.configure(
        "RegistroCardSubtitle.TLabel",
        background=blanco,
        foreground="#64748B",
        font=tipo(9),
    )
    estilo.configure(
        "RegistroField.TLabel",
        background=blanco,
        foreground="#1E293B",
        font=tipo(10, "bold"),
    )
    estilo.configure(
        "RegistroFieldIcon.TLabel",
        background=blanco,
        foreground="#64748B",
        font=tipo(11),
    )
    estilo.configure(
        "RegistroNotice.TLabel",
        background="#DBEAFE",
        foreground="#1D4ED8",
        font=tipo(9),
        padding=10,
    )
    estilo.configure("AccionEntrada.TFrame", background="#E7F8EE")
    estilo.configure(
        "AccionEntradaIcon.TLabel",
        background="#E7F8EE",
        foreground="#079447",
        font=tipo(16, "bold"),
    )
    estilo.configure(
        "AccionEntradaTitle.TLabel",
        background="#E7F8EE",
        foreground="#079447",
        font=tipo(10, "bold"),
    )
    estilo.configure(
        "AccionEntradaSub.TLabel",
        background="#E7F8EE",
        foreground="#3F8A5A",
        font=tipo(8),
    )
    estilo.configure("AccionSalida.TFrame", background="#FFF0F0")
    estilo.configure(
        "AccionSalidaIcon.TLabel",
        background="#FFF0F0",
        foreground="#D3323C",
        font=tipo(16, "bold"),
    )
    estilo.configure(
        "AccionSalidaTitle.TLabel",
        background="#FFF0F0",
        foreground="#D3323C",
        font=tipo(10, "bold"),
    )
    estilo.configure(
        "AccionSalidaSub.TLabel",
        background="#FFF0F0",
        foreground="#B45353",
        font=tipo(8),
    )
    estilo.configure("AccionDescanso.TFrame", background="#FFF5DC")
    estilo.configure(
        "AccionDescansoIcon.TLabel",
        background="#FFF5DC",
        foreground="#B97800",
        font=tipo(16, "bold"),
    )
    estilo.configure(
        "AccionDescansoTitle.TLabel",
        background="#FFF5DC",
        foreground="#B97800",
        font=tipo(10, "bold"),
    )
    estilo.configure(
        "AccionDescansoSub.TLabel",
        background="#FFF5DC",
        foreground="#A16207",
        font=tipo(8),
    )
    estilo.configure("AccionNeutro.TFrame", background="#F1F5F9")
    estilo.configure(
        "AccionNeutroIcon.TLabel",
        background="#F1F5F9",
        foreground="#64748B",
        font=tipo(16, "bold"),
    )
    estilo.configure(
        "AccionNeutroTitle.TLabel",
        background="#F1F5F9",
        foreground="#334155",
        font=tipo(10, "bold"),
    )
    estilo.configure(
        "AccionNeutroSub.TLabel",
        background="#F1F5F9",
        foreground="#64748B",
        font=tipo(8),
    )
    estilo.configure("PanelFooter.TFrame", background="#E9EFF7")
    estilo.configure(
        "PanelFooter.TLabel",
        background="#E9EFF7",
        foreground="#243456",
        font=tipo(9),
    )
    estilo.configure(
        "PanelFooterReady.TLabel",
        background="#E9EFF7",
        foreground="#079447",
        font=tipo(9, "bold"),
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
    """Aplica estilos de botones y aviso del formulario de registro."""

    configurar_estilos_registro(ventana)
    for nombre in ("id_empleado", "nombre_completo", "departamento", "accion",
                   "hora_inicio_prevista", "hora_fin_prevista", "observaciones"):
        builder.get_object(nombre).configure(font=tipo(11))
    builder.get_object("registrar_fichaje").configure(style="Primary.TButton")
    builder.get_object("limpiar_formulario").configure(style="Secondary.TButton")
    builder.get_object("aviso_fecha_hora").configure(style="RegistroNotice.TLabel")


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



def configurar_estilos_registro(ventana):
    """Tarjetas claras y controles amplios del formulario de jornada."""
    estilo = ttk.Style(ventana)
    azul, texto, borde = "#0866EE", "#101D48", "#D5DDE8"
    estilo.configure("RegistroPanel.TFrame", background="#FFFFFF",
                     borderwidth=1, relief="solid", bordercolor="#E4EAF2")
    estilo.configure("RegistroInput.TFrame", background="#FFFFFF",
                     borderwidth=1, relief="solid", bordercolor=borde)
    estilo.configure("RegistroInputIcon.TLabel", background="#FFFFFF",
                     foreground="#687384", font=tipo(14))
    for nombre in ("Registro.TEntry", "Registro.TCombobox", "Registro.TSpinbox"):
        estilo.configure(nombre, padding=(10, 9), fieldbackground="#FFFFFF",
                         foreground=texto, bordercolor=borde, lightcolor=borde,
                         darkcolor=borde, borderwidth=1, arrowsize=16, font=tipo(11))
        estilo.map(nombre, bordercolor=[("focus", azul)],
                   fieldbackground=[("readonly", "#F5F7FA")],
                   foreground=[("readonly", texto)])
    estilo.configure("RegistroAccion.TCombobox", padding=(12, 10),
                     foreground="#183C18", fieldbackground="#EFF9E5",
                     bordercolor="#CCE7B6", arrowsize=16, font=tipo(11))
    estilo.map("RegistroAccion.TCombobox",
               fieldbackground=[("readonly", "#EFF9E5")],
               foreground=[("readonly", "#183C18")],
               selectbackground=[("readonly", "#EFF9E5")],
               selectforeground=[("readonly", "#183C18")])
    estilo.configure("RegistroTitle.TLabel", font=tipo(18, "bold"))
    estilo.configure("RegistroSubtitle.TLabel", font=tipo(11))
    estilo.configure("RegistroClockDate.TLabel", font=tipo(10))
    estilo.configure("RegistroClockTime.TLabel", font=tipo(21, "bold"))
    estilo.configure("RegistroStatusCaption.TLabel", font=tipo(10))
    estilo.configure("RegistroStatusValue.TLabel", font=tipo(11, "bold"))
    estilo.configure("RegistroStatusDot.TLabel", font=tipo(20))
    estilo.configure("RegistroCardIcon.TLabel", background="#FFFFFF",
                     foreground="#0860CF", font=tipo(21, "bold"))
    estilo.configure("RegistroCardTitle.TLabel", font=tipo(14, "bold"))
    estilo.configure("RegistroCardSubtitle.TLabel", font=tipo(10))
    estilo.configure("RegistroField.TLabel", font=tipo(11))
    estilo.configure("RegistroNotice.TLabel", padding=(14, 8), font=tipo(10))
    estilo.configure("Primary.TButton", background=azul, padding=(18, 14),
                     font=tipo(12, "bold"))
    estilo.configure("Secondary.TButton", padding=(18, 14), font=tipo(12, "bold"))
    for nombre, fondo, acento in (("Entrada", "#ECF8DF", "#248B12"),
                                  ("Salida", "#FFF0F0", "#D3323C"),
                                  ("Descanso", "#FFF5DC", "#B97800"),
                                  ("Neutro", "#F1F5F9", "#64748B")):
        estilo.configure(f"Accion{nombre}.TFrame", background=fondo)
        for sufijo, tamano, peso in (("Icon", 24, "bold"),
                                      ("Title", 12, "bold"), ("Sub", 9, "normal")):
            estilo.configure(f"Accion{nombre}{sufijo}.TLabel", background=fondo,
                             foreground=acento, font=tipo(tamano, peso))
