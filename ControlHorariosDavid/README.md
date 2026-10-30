# Control de horarios de David

El proyecto está dividido en tres clases:

- `RepositorioExcel` (`repositorio_excel.py`) abre, lee y guarda `control_horarios_viajes.xlsx`.
- `ServicioFichajes` (`servicio_fichajes.py`) valida el empleado y la secuencia de acciones, y calcula los indicadores del día. No depende de la interfaz ni de Excel.
- `ControlHorariosApp` (`app.py`) lee los campos y coordina las otras dos clases. El bloque que construye las tres pestañas conserva la sangría y el formato originales para facilitar la revisión en Source Control.

Al pulsar **Registrar Fichaje**, la aplicación lee el formulario, pide al servicio que valide y prepare el registro, lo guarda mediante el repositorio y actualiza el panel y el histórico.

Desde esta carpeta se ejecuta con `uv run python app.py`. Las pruebas de lógica y Excel temporal se ejecutan con `uv run python -m unittest -q test_poo`.

Las copias intactas anteriores a la refactorización están en `backups/app_antes_poo_20261029.py` y `backups/control_horarios_viajes_antes_poo_20261029.xlsx`. El Excel de trabajo conserva su contenido anterior.
