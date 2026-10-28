"""Estado del empleado calculado a partir de sus fichajes, sin interfaz gráfica."""
from datetime import date, datetime, time, timedelta
import re


def _fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


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
