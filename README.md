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
4. La aplicación habilita solo el siguiente movimiento: **Entrar → Iniciar descanso → Fin descanso → Terminar jornada**. Su horario es el único editable. El botón junto a ese horario registra el fichaje; también puedes usar **Registrar fichaje**.
5. Comprueba las horas previstas. Los controles permiten escribir `HH:MM` o cambiar los minutos con sus flechas. Al cambiar de departamento, se consulta su horario en Excel.
6. Añade observaciones si las necesitas y pulsa **Registrar fichaje**.

La fecha y la hora del fichaje se toman del equipo automáticamente. Los campos marcados con asterisco son obligatorios. Tras guardar, el empleado permanece en el formulario y se habilita el siguiente paso. **Limpiar** vacía el formulario y los cuatro horarios; al elegir un departamento se cargan sus horas previstas.

### Validaciones

- Debes indicar ID, nombre completo, departamento y tipo de registro.
- Las horas previstas deben estar completas y usar el formato de 24 horas `HH:MM`, entre `00:00` y `23:59`.
- Los movimientos deben seguir el orden entrada, inicio de descanso, fin de descanso y salida.
- Tras terminar la jornada, no se puede iniciar otra el mismo día.

Si falta un dato o una hora no es válida, el formulario muestra un mensaje en español, marca el campo en rojo y sitúa allí el cursor. Si la secuencia de fichajes no es válida, se explica el motivo sin guardar el movimiento.

El indicador junto al calendario muestra **En jornada**, **En descanso**, **Jornada finalizada** o **Sin fichaje hoy**. Al cambiar de día, la ventana actualiza el estado y vuelve a permitir una entrada nueva. Un empleado cuyo primer fichaje sea futuro puede cargar sus datos, pero ese fichaje no activa su jornada antes de la hora indicada. También se contemplan turnos nocturnos con horario previsto que cruza la medianoche.

## Histórico

La pestaña **Histórico Excel** permite buscar por ID o nombre y filtrar por departamento, acción y rango de fechas. **Desde** y **Hasta** aceptan `dd/mm/aaaa` o se eligen con el calendario; cualquiera de los dos puede quedar vacío. Los extremos del rango están incluidos y se combinan con los demás filtros.

- Los fichajes aparecen inicialmente del más reciente al más antiguo. Pulsa cualquier encabezado para ordenar toda la lista; vuelve a pulsarlo para invertir el orden.
- Cada página muestra hasta **20 registros**. Usa **Inicio**, **Anterior**, **Siguiente** y **Final** para navegar.
- Las barras vertical y horizontal permiten recorrer las filas y columnas cuando no caben en pantalla.
- **Aplicar filtros** inicia la consulta desde la primera página.
- **Limpiar filtros** elimina las condiciones de búsqueda.
- **Actualizar histórico** vuelve a leer el Excel con los filtros actuales.

El pie indica el intervalo visible, el total de registros y la página actual. Consultar o filtrar no elimina datos.

La tabla lee el resultado guardado en la columna de fórmula **horas_trabajadas** del Excel en las filas de salida; no vuelve a calcularlo en la interfaz. El cumplimiento utiliza los mismos colores de estado definidos en Excel. Observaciones queda como última columna.

## Panel de control

Muestra los fichajes, entradas y salidas de hoy, las jornadas abiertas y los gráficos por día y por departamento. Puedes elegir períodos de 7, 14 o 30 días. Las jornadas abiertas se calculan a partir del último movimiento de entrada o salida de cada empleado.

Al cambiar de pestaña se actualiza la vista seleccionada. Al regresar al registro se recargan los departamentos y el estado del empleado. Tras guardar un fichaje también se actualizan el histórico y el panel.

## Archivo de Excel

El archivo utilizado es `data/control_horarios.xlsx`. Su ubicación se calcula desde la carpeta del proyecto, independientemente de la carpeta desde la que ejecutes la aplicación.

| Hoja          | Tabla              | Contenido                                                                                                                                                        |
| ------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Registros     | TablaRegistros     | Fichajes, cuatro horas previstas contiguas, fórmulas de diferencia y cumplimiento, cuatro horas reales contiguas y horas trabajadas netas en la fila de salida. |
| Departamentos | TablaDepartamentos | Departamento, hora de entrada, hora de salida, tolerancia en minutos, inicio y fin previstos del descanso.                                                       |

Conserva los encabezados: el programa los utiliza para identificar los campos. Las tablas permiten seleccionar columnas por su nombre y usar referencias como `TablaRegistros[hora]` en Excel. Al guardar un nuevo fichaje, la tabla se amplía y se conservan las fórmulas existentes.

La aplicación obtiene las horas previstas de la hoja **Departamentos**, sin mostrar el texto de las fórmulas en el histórico. Por ejemplo, **Idiomas** tiene horario de **08:00 a 13:00**.

En la fila de **Salida de Turno**, Excel calcula `horas_trabajadas = (salida_real - entrada_real) - (fin_descanso_real - inicio_descanso_real)`. Si no hay descanso registrado, descuenta cero; si falta la entrada o la salida, deja el resultado vacío. El resultado tiene formato de duración `[h]:mm`.

Al guardar desde la aplicación se calcula y conserva también el valor de la fórmula para que el Histórico pueda leerlo inmediatamente. Excel recalcula la fórmula al abrir el libro. Si modificas horas manualmente en Excel, guarda el libro después de recalcular y pulsa **Actualizar histórico**.

Guarda los cambios hechos en Excel para que la aplicación pueda leerlos. Evita guardar simultáneamente desde Excel y desde la aplicación. Las copias realizadas antes de sustituir los datos de prueba se encuentran en `data/backups/`.

## Datos de prueba para la presentación

El Excel actual contiene **118 fichajes**:

- 25 jornadas históricas de ejemplo con entrada, inicio y fin del descanso y salida, todas en orden cronológico.
- Dos jornadas completas registradas manualmente que se conservaron al ajustar los ejemplos.
- Diez entradas futuras a las 08:00 del departamento **Idiomas**, todavía sin descanso ni salida.
- Los empleados de esas diez entradas van de `EMP-013` a `EMP-022`. Por ejemplo, `EMP-022` corresponde a **Hugo Serrano**.

Los 118 registros ocupan seis páginas del histórico. La aplicación toma la fecha real del equipo para determinar el estado y los indicadores del día.

Para **sustituir los fichajes actuales** por un nuevo conjunto de 110 ejemplos:

```bash
uv run python generar_datos_prueba.py
```

Este comando guarda una copia anterior, conserva la hoja Departamentos y reemplaza los fichajes. Genera 100 registros de 25 jornadas completas entre ayer y hace 30 días, más 10 entradas para el día siguiente a su ejecución. Por tanto, ejecutarlo otro día cambia las fechas del conjunto de prueba.

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
