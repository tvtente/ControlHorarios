"""Estado del empleado calculado a partir de sus fichajes, sin interfaz gráfica."""
from datetime import date, datetime, time, timedelta
import re
import unicodedata


def _fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def interpretar_rango_fechas(desde="", hasta=""):
    """Convierte fechas del filtro (dd/mm/aaaa) y comprueba el orden."""
    def convertir(valor, etiqueta):
        valor = valor.strip()
        if not valor:
            return None
        try:
            resultado = datetime.strptime(valor, "%d/%m/%Y").date()
            if resultado.strftime("%d/%m/%Y") != valor:
                raise ValueError
            return resultado
        except ValueError:
            raise ValueError(f"{etiqueta}: escribe una fecha válida con formato dd/mm/aaaa.") from None

    inicio = convertir(desde, "Desde")
    fin = convertir(hasta, "Hasta")
    if inicio and fin and inicio > fin:
        raise ValueError("La fecha «Desde» no puede ser posterior a «Hasta».")
    return inicio, fin


def filtrar_fichajes_por_fecha(registros, desde=None, hasta=None):
    """Incluye los extremos del rango y omite fechas ausentes o inválidas."""
    if desde is None and hasta is None:
        return registros
    resultado = []
    for registro in registros:
        fecha = _fecha(registro.get("fecha"))
        if fecha is not None and (desde is None or fecha >= desde) and (hasta is None or fecha <= hasta):
            resultado.append(registro)
    return resultado


def _hora(valor):
    if isinstance(valor, datetime):
        return valor.time()
    if isinstance(valor, time):
        return valor
    try:
        return time.fromisoformat(str(valor).strip())
    except ValueError:
        return None


def normalizar_id_empleado(valor):
    """Ignora mayúsculas y separadores habituales del ID de empleado."""
    return re.sub(r"[-_\s]+", "", str(valor or "")).casefold()


def estado_empleado(registros, empleado, *, ahora=None):
    """Busca un ID exacto y diferencia presencia, descanso y salida."""
    ahora = ahora or datetime.now()
    clave = normalizar_id_empleado(empleado)
    coincidencias = []
    for orden, registro in enumerate(registros):
        if not clave or normalizar_id_empleado(registro.get('id_empleado')) != clave:
            continue
        fecha = _fecha(registro.get('fecha'))
        hora = _hora(registro.get('hora')) or time.min
        if fecha is not None:
            coincidencias.append((datetime.combine(fecha, hora), orden, registro))
    if not coincidencias:
        return {'texto': 'Sin fichaje', 'color': '#94A3B8', 'empleado': None}
    coincidencias.sort(key=lambda r: (r[0], r[1]))
    perfil = coincidencias[-1][2]
    resultado = {'texto': 'Sin fichaje hoy', 'color': '#94A3B8', 'empleado': perfil}
    for instante, _, registro in reversed(coincidencias):
        if instante > ahora:
            continue
        accion = str(registro.get('accion') or '').strip().casefold()
        if accion not in ('entrada', 'entrada a turno', 'salida', 'salida de turno',
                          'inicio de descanso', 'fin de descanso'):
            continue
        inicio = _hora(registro.get('hora_inicio_prevista'))
        fin = _hora(registro.get('hora_fin_prevista'))
        nocturno = (instante.date() == ahora.date() - timedelta(days=1)
                    and inicio is not None and fin is not None and inicio > fin
                    and ahora.time() <= fin)
        if instante.date() != ahora.date() and not nocturno:
            break
        if accion in ('salida', 'salida de turno'):
            resultado.update(texto='Jornada finalizada', color='#64748B')
        elif accion == 'inicio de descanso':
            resultado.update(texto='En descanso', color='#B97800')
        else:
            resultado.update(texto='En jornada', color='#079447')
        break
    return resultado


def siguiente_fichaje(registros, empleado, *, ahora=None):
    """Indica el único movimiento permitido en la jornada actual."""
    ahora = ahora or datetime.now()
    estado = estado_empleado(registros, empleado, ahora=ahora)["texto"]
    if estado in ("Sin fichaje", "Sin fichaje hoy"):
        return "Entrada a Turno"
    if estado == "En descanso":
        return "Fin de Descanso"
    if estado == "Jornada finalizada":
        return None

    clave = normalizar_id_empleado(empleado)
    movimientos = []
    for orden, registro in enumerate(registros):
        if normalizar_id_empleado(registro.get("id_empleado")) != clave:
            continue
        fecha = _fecha(registro.get("fecha"))
        if fecha is None:
            continue
        instante = datetime.combine(fecha, _hora(registro.get("hora")) or time.min)
        if instante <= ahora:
            movimientos.append((instante, orden, str(registro.get("accion") or "").strip().casefold()))
    if not movimientos:
        return "Entrada a Turno"
    ultima = max(movimientos)[2]
    return "Salida de Turno" if ultima == "fin de descanso" else "Inicio de Descanso"


def validar_fichaje(registros, empleado, accion, *, ahora=None):
    """Exige entrada, inicio/fin de descanso y salida, en ese orden."""
    aliases = {'entrada': 'Entrada a Turno', 'salida': 'Salida de Turno'}
    accion = aliases.get(accion.strip().casefold(), accion.strip())
    if accion not in ('Entrada a Turno', 'Inicio de Descanso', 'Fin de Descanso', 'Salida de Turno'):
        raise ValueError('Selecciona un tipo de registro válido.')
    siguiente = siguiente_fichaje(registros, empleado, ahora=ahora)
    if siguiente is None:
        raise ValueError('La jornada de hoy ya terminó. Podrás registrar otra entrada el próximo día.')
    if accion != siguiente:
        raise ValueError(f'El siguiente movimiento permitido es «{siguiente}».')


def clave_orden_fichaje(registro):
    """Orden cronológico compatible con fechas y horas de texto o de Excel."""
    fecha = _fecha(registro.get('fecha')) or date.min
    hora = _hora(registro.get('hora')) or time.min
    try:
        identificador = int(registro.get('id_registro') or 0)
    except (TypeError, ValueError):
        identificador = 0
    return datetime.combine(fecha, hora), identificador


def ordenar_fichajes(registros, columna="fecha", descendente=True):
    """Ordena todos los fichajes antes de paginar, con vacíos siempre al final."""
    ordenados = sorted(registros, key=clave_orden_fichaje, reverse=True)

    def clave(registro):
        valor = registro.get(columna)
        if columna == "id_registro":
            try:
                return int(valor)
            except (TypeError, ValueError):
                return None
        if columna == "fecha":
            fecha = _fecha(valor)
            hora = _hora(registro.get("hora")) or time.min
            return (fecha, hora) if fecha else None
        if columna == "hora" or columna.startswith("hora_"):
            return _hora(valor)
        if columna == "horas_trabajadas":
            try:
                horas, minutos = str(valor).split(":", 1)
                return int(horas) * 60 + int(minutos)
            except (AttributeError, TypeError, ValueError):
                return None
        if valor in (None, ""):
            return None
        texto = unicodedata.normalize("NFKD", str(valor).casefold())
        return "".join(c for c in texto if not unicodedata.combining(c))

    presentes = [r for r in ordenados if clave(r) is not None]
    ausentes = [r for r in ordenados if clave(r) is None]
    return sorted(presentes, key=clave, reverse=descendente) + ausentes
