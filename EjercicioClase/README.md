# Ejercicio de clase: Pygubu con dos pestañas independientes

Esta demo registra personas **solo en memoria** para enseñar cómo dividir una aplicación Pygubu. Al cerrar la ventana, los datos se pierden: así podemos concentrarnos en los archivos UI, las clases y sus callbacks.

## Preparar el entorno y ejecutar (sin uv)

Abre una terminal **dentro de `EjercicioClase`**, donde está `app.py`.
Necesitas Python 3.10 o posterior con Tkinter. Crea el entorno una sola vez y actívalo en cada terminal nueva.

### Windows: CMD

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

### Windows: PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes usar CMD con el comando anterior.
En Windows se utiliza `activate`, no `source`.

### macOS y Linux: bash o zsh

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Con el entorno activado: igual en los tres sistemas

```bash
python -m pip install pygubu-designer ttkbootstrap
python app.py
```

No necesitas requirements.txt: instala directamente `pygubu-designer` (incluye la biblioteca `pygubu`) y `ttkbootstrap` (temas y estilos). Tkinter forma parte de la biblioteca estándar de Python y debe estar disponible en su instalación. La instalación se realiza una vez por entorno.
Comprueba qué intérprete estás usando con `python -c "import sys; print(sys.executable)"`:
debe apuntar a `.venv` dentro de este ejercicio. Para salir del entorno: `deactivate`.
El entorno de este ejercicio es independiente del de la carpeta superior.

Para inspeccionar cada diseño:

```bash
pygubu-designer ui/principal.ui
pygubu-designer ui/formulario.ui
pygubu-designer ui/tabla.ui
```

También puedes abrir el Designer una vez y cambiar de archivo mediante **Archivo → Abrir**.
`principal.ui` contiene las pestañas; los controles están en `formulario.ui` y `tabla.ui`.

Para comprobar que Tkinter está disponible: `python -m tkinter`.
Si falta en Linux, instala el paquete Tkinter de tu distribución; si falta el módulo `venv`, instala también su paquete correspondiente.

## Reparto de responsabilidades

| Archivo | Qué contiene |
| --- | --- |
| `ui/principal.ui` | El `Notebook` con las pestañas **Formulario** y **Tabla de personas** |
| `ui/formulario.ui` | `Entry`, `Combobox`, `Spinbox`, `Radiobutton`, `Checkbutton`, `Text` y botones |
| `ui/tabla.ui` | Búsqueda, `Treeview`, eliminación, contador y `Progressbar` |
| `formulario.py` | Clase `PestanaFormulario`: lee, valida y limpia los controles del formulario |
| `tabla.py` | Clase `PestanaTabla`: filtra y muestra filas; comunica qué ID se quiere eliminar |
| `app.py` | Clase `DemoPygubu`: crea la ventana, reúne las pestañas y posee `personas` |
| `styles/__init__.py` | Tema y estilos compartidos por ambas pestañas |
| `images/icono.png` | Icono que muestra la ventana de la demostración |
| `images/registro_animado.gif` | GIF que aparece encima del formulario |

El archivo anterior de una sola pantalla queda en `backups/demo_una_pantalla.ui` para comparar ambos diseños.

## Cómo se unen las tres UI

1. `DemoPygubu` usa un `pygubu.Builder` para cargar `principal.ui`
2. Obtiene `contenedor_formulario` y `contenedor_tabla` del `Notebook`
3. `PestanaFormulario` carga `formulario.ui` dentro del primer contenedor
4. `PestanaTabla` carga `tabla.ui` dentro del segundo
5. Cada clase llama a `connect_callbacks(self)` **sobre su propio Builder**

Por eso un botón de `formulario.ui` puede llamar a `PestanaFormulario.guardar_persona`, mientras que el botón de `tabla.ui` llama a `PestanaTabla.eliminar_persona`. No hace falta generar un único archivo Python gigante desde Pygubu.

## Flujo de un registro

```text
Botón «Añadir a la tabla» (formulario.ui)
    → PestanaFormulario lee y valida los campos
    → DemoPygubu recibe los datos y les asigna un ID
    → DemoPygubu actualiza PestanaTabla
    → La aplicación selecciona la pestaña de la tabla
```

La lista `personas` vive en `DemoPygubu`. Las pestañas no comparten controles directamente: se comunican a través de la aplicación principal. Al eliminar, `PestanaTabla` entrega el ID seleccionado y `DemoPygubu` quita ese registro de la lista.

## Commands y bindings

- **Command:** los botones `guardar`, `limpiar` y `eliminar` declaran en su UI el nombre del método que se ejecuta al pulsarlos
- **Binding:** `buscar` declara `<KeyRelease>` para filtrar mientras escribes; `categoria` declara `<<ComboboxSelected>>`; `tabla` declara `<<TreeviewSelect>>`; el `Notebook` declara `<<NotebookTabChanged>>`
- Los métodos de un binding reciben el evento como argumento (`_evento`); los commands simples no lo reciben

## Cómo se añade un GIF animado

En `ui/formulario.ui` hay un `ttk.Label` llamado `imagen_animada`. Su propiedad **image** apunta a `../images/registro_animado.gif`: así se ve y se puede colocar desde Pygubu Designer. En `formulario.py`, el Builder registra la carpeta `images/` como ruta de recursos.

Pygubu coloca la imagen, pero **no reproduce automáticamente los fotogramas**. Por eso `PestanaFormulario._iniciar_animacion()` carga cada fotograma con `tk.PhotoImage(..., format="gif -index N")`, conserva las imágenes en `self._fotogramas` y `_mostrar_siguiente_fotograma()` cambia el `Label` cada 650 ms con `after()`. El GIF mide 740 × 120 píxeles, como una franja horizontal. El binding `<Destroy>` del Label llama a `detener_animacion()` al cerrar la ventana.

El GIF está incluido y la aplicación no necesita Pillow para mostrarlo. Si quieres **regenerar el archivo** a partir de sus dibujos, ejecuta `python images/crear_gif.py` con el entorno activado e instala antes Pillow con `python -m pip install Pillow`; esa utilidad sí usa Pillow.

## Para practicar en clase

1. Cambia el título o el color de un botón en `formulario.ui`
2. Añade una opción al `Combobox` de categoría
3. Registra tres personas y filtra por nombre o categoría en la otra pestaña
4. Selecciona una fila y elimínala
5. Como ampliación, guarda `DemoPygubu.personas` en JSON y cárgala al iniciar

**Importante:** si cambias un ID de widget o el nombre de un callback en Designer, actualiza también su referencia en la clase Python correspondiente.
