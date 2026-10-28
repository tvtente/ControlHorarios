# Control de horarios

Aplicación de escritorio para registrar entradas, salidas y descansos, consultar fichajes y visualizar la actividad laboral. Está desarrollada con Python, Tkinter, ttkbootstrap, Pygubu y openpyxl. Los datos se guardan en un archivo de Excel.

## Instalación y ejecución

Necesitas Python 3.10 o posterior con Tkinter y [uv](https://docs.astral.sh/uv/getting-started/installation/). Desde la carpeta del proyecto:

```bash
uv sync
uv run python main.py
```

`uv sync` instala las dependencias declaradas en `pyproject.toml` y fijadas en `uv.lock`. El entorno local se crea en `.venv`.

### Fuentes en Linux

Si las letras aparecen pixeladas, utiliza el Python del sistema con Tkinter instalado:

```bash
uv sync --python /usr/bin/python3
uv run python main.py
```

La aplicación selecciona Noto Sans o DejaVu Sans cuando están disponibles. Esta instalación utiliza Tk 8.6 para evitar la sustitución de esas fuentes por una fuente de píxeles.

## Registro de fichajes

1. Introduce el ID del empleado. La sugerencia `EMP-000` solo indica el formato: no es un valor del formulario.
2. Pulsa **Tab** o **Intro**. Si el empleado tiene registros en el Excel, se cargan su nombre, departamento y horario previsto. Se reconocen como el mismo ID `emp001`, `EMP001` y `EMP-001`.
3. Para un empleado nuevo, escribe su nombre completo y selecciona un departamento.
4. Selecciona el tipo de registro: entrada de turno, salida de turno, inicio de descanso o fin de descanso.
5. Comprueba las horas previstas. Los controles permiten escribir `HH:MM` o cambiar los minutos con sus flechas. Al cambiar de departamento, se consulta su horario en Excel.
6. Añade observaciones si las necesitas y pulsa **Registrar fichaje**.

La fecha y la hora del fichaje se toman del equipo automáticamente. Los campos marcados con asterisco son obligatorios. **Limpiar** vacía el formulario y restablece las horas iniciales de 08:00 y 17:00; al elegir un departamento se cargan sus horas reales.

### Validaciones

- Debes indicar ID, nombre completo, departamento y tipo de registro.
- Las horas previstas deben estar completas y usar el formato de 24 horas `HH:MM`, entre `00:00` y `23:59`.
- No se puede registrar otra entrada mientras exista una jornada abierta.
- La salida necesita una entrada previa y no puede registrarse durante un descanso sin finalizar.
- Solo se puede iniciar un descanso durante una jornada abierta y sin otro descanso activo.
- Solo se puede finalizar un descanso que esté abierto.

Si falta un dato o una hora no es válida, el formulario muestra un mensaje en español, marca el campo en rojo y sitúa allí el cursor. Si la secuencia de fichajes no es válida, se explica el motivo sin guardar el movimiento.

El indicador junto al calendario muestra **En jornada**, **En descanso**, **Jornada finalizada** o **Sin fichaje hoy**. Un empleado cuyo primer fichaje sea futuro puede cargar sus datos, pero ese fichaje no activa su jornada antes de la hora indicada. También se contemplan turnos nocturnos con horario previsto que cruza la medianoche.

## Histórico

La pestaña **Histórico Excel** permite buscar por ID o nombre y filtrar por departamento y acción.

- Los fichajes se ordenan por fecha y hora, del más reciente al más antiguo.
- Cada página muestra hasta **20 registros**. Usa **Anterior** y **Siguiente** para navegar.
- Las barras vertical y horizontal permiten recorrer las filas y columnas cuando no caben en pantalla.
- **Aplicar filtros** inicia la consulta desde la primera página.
- **Limpiar filtros** elimina las condiciones de búsqueda.
- **Actualizar histórico** vuelve a leer el Excel con los filtros actuales.

El pie indica el intervalo visible, el total de registros y la página actual. Consultar o filtrar no elimina datos.

## Panel de control

Muestra los fichajes, entradas y salidas de hoy, las jornadas abiertas y los gráficos por día y por departamento. Puedes elegir períodos de 7, 14 o 30 días. Las jornadas abiertas se calculan a partir del último movimiento de entrada o salida de cada empleado.

Al cambiar de pestaña se actualiza la vista seleccionada. Al regresar al registro se recargan los departamentos y el estado del empleado. Tras guardar un fichaje también se actualizan el histórico y el panel.

## Archivo de Excel

El archivo utilizado es `data/control_horarios.xlsx`. Su ubicación se calcula desde la carpeta del proyecto, independientemente de la carpeta desde la que ejecutes la aplicación.

| Hoja | Tabla | Contenido |
| --- | --- | --- |
| Registros | TablaRegistros | Fichajes, horas previstas y fórmulas de diferencia y cumplimiento. |
| Departamentos | TablaDepartamentos | Departamento, hora de entrada, hora de salida y tolerancia en minutos. |

Conserva los encabezados: el programa los utiliza para identificar los campos. Las tablas permiten seleccionar columnas por su nombre y usar referencias como `TablaRegistros[hora]` en Excel. Al guardar un nuevo fichaje, la tabla se amplía y se conservan las fórmulas existentes.

La aplicación obtiene las horas previstas de la hoja **Departamentos**, sin mostrar el texto de las fórmulas en el histórico. Por ejemplo, **Idiomas** tiene horario de **08:00 a 13:00**.

Guarda los cambios hechos en Excel para que la aplicación pueda leerlos. Evita guardar simultáneamente desde Excel y desde la aplicación. Las copias realizadas antes de sustituir los datos de prueba se encuentran en `data/backups/`.

## Datos de prueba para la presentación

El conjunto preparado el **28 de octubre de 2026** contiene **60 fichajes**:

- 50 fichajes de jornadas distribuidas entre el **29 de septiembre y el 28 de octubre de 2026**.
- Los 10 últimos son entradas del **29 de octubre de 2026 a las 08:00**, del departamento **Idiomas**, con horario previsto de **08:00 a 13:00**.
- Los empleados de esas diez entradas van de `EMP-013` a `EMP-022`. Por ejemplo, `EMP-022` corresponde a **Hugo Serrano**.

Los 60 registros ocupan tres páginas del histórico. La aplicación toma la fecha real del equipo para determinar el estado y los indicadores del día.

Para **sustituir los fichajes actuales** por un nuevo conjunto de 60 ejemplos:

```bash
uv run python generar_datos_prueba.py
```

Este comando guarda una copia anterior, conserva la hoja Departamentos y reemplaza los fichajes. Genera 50 registros de los últimos 30 días y 10 entradas para el día siguiente a su ejecución. Por tanto, ejecutarlo otro día cambia las fechas del conjunto de prueba.

## Diseño de las pantallas

Los diseños se editan por separado:

```bash
uv run pygubu-designer ui/registro.ui
uv run pygubu-designer ui/panel.ui
uv run pygubu-designer ui/historico.ui
uv run pygubu-designer ui/control_horarios.ui
```

`control_horarios.ui` contiene las pestañas y el pie común. `main.py` carga las tres pantallas en sus contenedores, conecta sus eventos y busca los iconos en `images/`. Los estilos y la selección de fuentes están en `styles/__init__.py`.

## Uso desde la consola

```bash
uv run python consola.py
```

Puedes registrar o consultar fichajes. La consola utiliza el mismo archivo de Excel y las mismas validaciones de secuencia que la interfaz gráfica.

## Compartir el proyecto

Incluye los módulos Python, `ui/`, `images/`, `pyproject.toml`, `uv.lock` y este documento. Añade `data/control_horarios.xlsx` si quieres compartir también los datos preparados para la demostración. No compartas `.venv`: cada equipo debe crear su propio entorno con `uv sync`.
