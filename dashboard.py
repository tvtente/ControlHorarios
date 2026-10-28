"""Métricas y gráficos del panel calculados desde los fichajes de Excel."""

from collections import Counter
from datetime import date, datetime, timedelta
from math import ceil


ENTRADA = "Entrada a Turno"
SALIDA = "Salida de Turno"


def _fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor.strip()[:10])
        except ValueError:
            return None
    return None


def build_dashboard_data(registros, *, hoy=None, dias=7):
    """Resume registros sin modificar el libro ni depender de Tkinter."""
    hoy = hoy or date.today()
    inicio = hoy - timedelta(days=dias - 1)
    por_dia = {inicio + timedelta(days=i): Counter() for i in range(dias)}
    departamentos = Counter()
    acciones_actuales = {}
    fichajes_hoy = entradas_hoy = salidas_hoy = 0

    for orden, registro in enumerate(registros):
        fecha = _fecha(registro.get("fecha"))
        if fecha is None or fecha > hoy:
            continue
        accion = str(registro.get("accion") or "").strip()
        empleado = str(registro.get("id_empleado") or "").strip().casefold()
        departamento = str(registro.get("departamento") or "").strip()
        if departamento:
            departamentos[departamento] += 1

        if fecha == hoy:
            fichajes_hoy += 1
            entradas_hoy += accion == ENTRADA
            salidas_hoy += accion == SALIDA
        if fecha in por_dia and accion in (ENTRADA, SALIDA):
            por_dia[fecha][accion] += 1

        if empleado and accion in (ENTRADA, SALIDA):
            clave = (fecha.isoformat(), str(registro.get("hora") or ""), orden)
            anterior = acciones_actuales.get(empleado)
            if anterior is None or clave > anterior[0]:
                acciones_actuales[empleado] = (clave, accion)

    return {
        "fichajes_hoy": fichajes_hoy,
        "entradas_hoy": entradas_hoy,
        "salidas_hoy": salidas_hoy,
        "jornadas_abiertas": sum(
            accion == ENTRADA for _, accion in acciones_actuales.values()
        ),
        "dias": [
            (dia, por_dia[dia][ENTRADA], por_dia[dia][SALIDA])
            for dia in por_dia
        ],
        "departamentos": departamentos.most_common(),
    }


def dibujar_fichajes_por_dia(canvas, filas):
    """Dibuja dos series de barras en un Canvas redimensionable."""
    canvas.delete("all")
    ancho, alto = canvas.winfo_width(), canvas.winfo_height()
    if ancho < 120 or alto < 120:
        return
    color_texto, color_grid = "#243456", "#DDE7F2"
    izquierda, derecha, arriba, abajo = 45, 14, 45, 48
    base = alto - abajo
    area = max(1, base - arriba)
    maximo = max((max(entrada, salida) for _, entrada, salida in filas), default=0)
    escala = max(4, ceil(maximo / 4) * 4)

    canvas.create_rectangle(izquierda + 2, 11, izquierda + 13, 22, fill="#20A45B", outline="")
    canvas.create_text(izquierda + 19, 16, text="Entradas", anchor="w", fill=color_texto,
                       font=("Segoe UI", 9))
    canvas.create_rectangle(izquierda + 106, 11, izquierda + 117, 22, fill="#E3454D", outline="")
    canvas.create_text(izquierda + 123, 16, text="Salidas", anchor="w", fill=color_texto,
                       font=("Segoe UI", 9))

    for paso in range(5):
        valor = escala * paso // 4
        y = base - area * paso / 4
        canvas.create_line(izquierda, y, ancho - derecha, y, fill=color_grid)
        canvas.create_text(izquierda - 7, y, text=str(valor), anchor="e", fill=color_texto,
                           font=("Segoe UI", 9))

    if maximo == 0:
        canvas.create_text(ancho / 2, (arriba + base) / 2, text="Sin fichajes en este período",
                           fill="#62748A", font=("Segoe UI", 11))
        return

    espacio = max(1, (ancho - izquierda - derecha) / len(filas))
    barra = max(2, min(17, espacio * 0.28))
    mostrar_cada = max(1, (len(filas) + 7) // 8)
    for indice, (dia, entradas, salidas) in enumerate(filas):
        centro = izquierda + espacio * (indice + 0.5)
        for desplazamiento, valor, color in ((-barra - 1, entradas, "#20A45B"),
                                             (1, salidas, "#E3454D")):
            if valor == 0:
                continue
            x1 = centro + desplazamiento
            y1 = base - (valor / escala) * area
            canvas.create_rectangle(x1, y1, x1 + barra, base, fill=color, outline="")
            if valor and len(filas) <= 14 and espacio >= 25:
                canvas.create_text(x1 + barra / 2, y1 - 7, text=str(valor),
                                   fill=color_texto, font=("Segoe UI", 8))
        if indice % mostrar_cada == 0 or indice == len(filas) - 1:
            canvas.create_text(centro, base + 15, text=dia.strftime("%d/%m"),
                               fill=color_texto, font=("Segoe UI", 8))


def dibujar_departamentos(canvas, filas):
    """Dibuja los seis departamentos más activos y agrupa el resto."""
    canvas.delete("all")
    ancho, alto = canvas.winfo_width(), canvas.winfo_height()
    if ancho < 120 or alto < 120:
        return
    if not filas:
        canvas.create_text(ancho / 2, alto / 2, text="Sin fichajes por departamento",
                           fill="#62748A", font=("Segoe UI", 11))
        return
    visibles = list(filas[:6])
    if len(filas) > 6:
        visibles.append(("Otros", sum(valor for _, valor in filas[6:])))
    maximo = max(valor for _, valor in visibles)
    izquierda, derecha = min(165, max(110, ancho * 0.34)), 44
    espacio = (alto - 44) / len(visibles)
    for indice, (nombre, valor) in enumerate(visibles):
        y = 22 + espacio * (indice + 0.5)
        etiqueta = nombre if len(nombre) <= 20 else nombre[:18] + "…"
        canvas.create_text(izquierda - 12, y, text=etiqueta, anchor="e", fill="#243456",
                           font=("Segoe UI", 9))
        largo = max(2, (ancho - izquierda - derecha) * valor / maximo)
        canvas.create_rectangle(izquierda, y - 10, izquierda + largo, y + 10,
                                fill="#2D7CF2", outline="")
        canvas.create_text(izquierda + largo + 7, y, text=str(valor), anchor="w",
                           fill="#243456", font=("Segoe UI", 9, "bold"))
