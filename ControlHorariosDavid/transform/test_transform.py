"""Verificaciones del flujo sin modificar el Excel de trabajo."""

import datetime
import tempfile
import unittest

from excel.gestor_excel import GestorExcel
from logica.gestor_fichajes import GestorFichajes


class TransformTest(unittest.TestCase):
    def test_fichaje_y_nueva_jornada(self):
        with tempfile.TemporaryDirectory() as carpeta:
            excel = GestorExcel(carpeta)
            gestor = GestorFichajes(excel)
            ayer = datetime.datetime(2026, 10, 28, 9)
            hoy = datetime.datetime(2026, 10, 29, 9)
            gestor.guardar_fichaje_excel("EMP-001", "Ana", "Ventas",
                                         "Entrada a Turno", "", ayer)
            gestor.guardar_fichaje_excel("EMP-001", "Ana", "Ventas",
                                         "Entrada a Turno", "", hoy)
            registros = excel.obtener_registros_excel()
            self.assertEqual(len(registros), 2)
            self.assertEqual(gestor.obtener_estado_actual("EMP-001", registros,
                                                          hoy.date()), "Trabajando")
            self.assertEqual(gestor.calcular_empleados_hoy(registros, hoy.date()), 1)
            self.assertEqual(gestor.calcular_departamentos(registros, hoy.date()), 1)
            with self.assertRaises(ValueError):
                gestor.guardar_fichaje_excel("EMP-001", "Otra", "Ventas",
                                             "Salida a Pausa", "", hoy)
            with self.assertRaises(ValueError):
                gestor.guardar_fichaje_excel("EMP-001", "Ana", "Ventas",
                                             "Entrada a Turno", "", hoy)
            gestor.guardar_fichaje_excel("EMP-001", "Ana", "Ventas",
                                         "Salida a Pausa", "", hoy)
            self.assertEqual(len(excel.obtener_registros_excel()), 3)


if __name__ == "__main__":
    unittest.main()
