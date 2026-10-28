# Control de horarios

Desktop application built with ttkbootstrap (`cosmo` theme), a Pygubu UI file, and openpyxl.

## Why we use uv

`uv` manages Python dependencies and virtual environments. It creates a separate `.venv` for this project, keeping its packages isolated from other projects.

It helps us work together because:

- `pyproject.toml` declares the project dependencies.
- `uv.lock` records the resolved package versions, making installations reproducible across our computers.
- `uv sync` creates or updates the environment automatically.
- `uv run` runs a command in the project environment without manual activation.

This gives us a shared setup for Pygubu Designer, ttkbootstrap, and openpyxl.

### Sharing the project

Share the project files, including `pyproject.toml`, `uv.lock`, and the `ui` folder. Leave out `.venv`: virtual environments contain machine-specific paths and should be recreated on the receiving computer.

Install uv using the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/), then open a terminal in the project folder and run the commands below. `uv sync` recreates the environment from the shared configuration.

`openpyxl` and `ttkbootstrap` are included in the project dependencies.

Reference: [uv project documentation](https://docs.astral.sh/uv/guides/projects/).

## Open the UI designer

Each screen can be edited independently. `control_horarios.ui` contains only the notebook and its three empty containers; `main.py` loads the corresponding screen into each container at runtime.

```bash
uv sync
uv run pygubu-designer ui/registro.ui
uv run pygubu-designer ui/panel.ui
uv run pygubu-designer ui/historico.ui
```

To edit the common notebook and tab labels:

```bash
uv run pygubu-designer ui/control_horarios.ui
```

## Run the application

`main.py` loads all four `.ui` files using Pygubu and opens the assembled desktop window.

```bash
uv run python main.py
```

Share `main.py`, `ui/`, `pyproject.toml`, and `uv.lock`; exclude `.venv`. After installing uv, your teammate can run the same command to create the environment and open the application. Python must support Tkinter.

The registration form and history table are connected to Excel through `ExcelManager` and Pygubu callbacks.

### Regenerate with Pygubu Designer (optional)

In **Project Settings**, select **Application that uses UI file**, main widget `app`, and a different module name (for example, `generated_app`). Choose the project root as output directory, enable **Regenerate code when saving the project**, and save. The generator produces a launcher and a companion UI module; keep both files.

## Excel connection

`main.py` uses `ExcelManager` from `excel_manager.py`. The application automatically creates the `data/` folder and stores the workbook at `data/control_horarios_viajes.xlsx`. The location is relative to `main.py`, regardless of the terminal working directory.

- **Registrar fichaje** saves the form values, clears the form after success, and refreshes the history.
- **Aplicar filtros** searches by employee, department, and action.
- **Limpiar filtros** shows all saved records.
- **Actualizar histórico** reloads records using the current filters.
- **Limpiar** clears only the registration form.

These buttons are connected through Pygubu `command` callbacks. Refreshing the table never deletes records from Excel.

## Dashboard

The dashboard now reads the same workbook: it shows today's records, shift starts and ends, and employees whose latest shift movement is an entry. Its charts compare entries and exits over the last 7, 14, or 30 days and show total records by department. The **Actualizar** button reloads the Excel data; a successful registration also refreshes the dashboard automatically.

The console program is also available and uses the same workbook as the GUI:

```bash
uv run python consola.py
```

Run the GUI with `uv run python main.py`. Use one application at a time when saving to the shared workbook.
