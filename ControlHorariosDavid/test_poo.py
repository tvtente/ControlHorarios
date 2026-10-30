"""Pruebas de las reglas y del repositorio sin abrir la interfaz."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from repositorio_excel import RepositorioExcel
from servicio_fichajes import ServicioFichajes


class ControlHorariosPOOTest(unittest.TestCase):
    def test_repositorio_guardar_y_leer(self):
        with tempfile.TemporaryDirectory() as carpeta:
            repo = RepositorioExcel(Path(carpeta) / "prueba.xlsx")
            self.assertEqual(repo.obtener_registros_excel(), [])
            fila = ["EMP-001", "Ana", "Ventas", "Entrada a Turno",
                    "29-10-2026", "09:00:00", ""]
            repo.guardar_excel(fila)
            self.assertEqual(list(repo.obtener_registros_excel()[0]), fila[:-1] + [None])

    def test_jornada_nueva_y_validaciones(self):
        servicio = ServicioFichajes()
        ayer = [["EMP-001", "Ana", "Ventas", "Entrada a Turno",
                 "28-10-2026", "09:00:00", ""]]
        ahora = datetime(2026, 10, 29, 9)
        fila = servicio.crear_registro("EMP-001", "Ana", "Ventas",
                                      "Entrada a Turno", "", ayer, ahora)
        self.assertEqual(fila[4:6], ["29-10-2026", "09:00:00"])
        with self.assertRaises(ValueError):
            servicio.crear_registro("EMP-001", "Otra", "Ventas",
                                    "Entrada a Turno", "", ayer, ahora)
        with self.assertRaises(ValueError):
            servicio.crear_registro("EMP-001", "Ana", "Ventas",
                                    "Salida de Turno", "", ayer, ahora)
        self.assertEqual(servicio.obtener_estado_empleado("EMP-001", ayer + [fila],
                                                         ahora.date()), "Trabajando")


if __name__ == "__main__":
    unittest.main()
