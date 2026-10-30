# Versión orientada a objetos (`transform`)

Esta carpeta conserva el Excel y la interfaz de tres pestañas del proyecto original. Las responsabilidades están separadas así:

- `excel/gestor_excel.py`: `GestorExcel` crea, lee y guarda `control_horarios_viajes.xlsx` en esta carpeta.
- `logica/gestor_fichajes.py`: `GestorFichajes` valida los campos, la identidad y la secuencia de fichajes; calcula los indicadores del día.
- `interfaz/registrar.py`, `panel.py` e `historico.py`: cada pestaña construye y actualiza solo sus propios widgets.
- `app.py`: `App` conecta las pestañas con la lógica y muestra los mensajes al usuario.
- `config.py`: opciones de los controles y transiciones de estado compartidas.

Desde esta carpeta: `uv run python app.py`. Para verificar la lógica con un Excel temporal: `uv run python -m unittest -q test_transform`.

El respaldo de los archivos encontrados antes de esta revisión está en `backups/antes_revision_20261029/`. `app_antigua.py` también permanece sin cambios. El Excel de trabajo no se modificó durante la refactorización.
