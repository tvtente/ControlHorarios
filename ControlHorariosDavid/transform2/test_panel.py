import datetime
import unittest

from logica.gestor_fichajes import GestorFichajes


class PanelTest(unittest.TestCase):
    def test_empleados_y_departamentos_distintos_de_hoy(self):
        hoy = datetime.date.today().strftime("%d-%m-%Y")
        ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        registros = [
            ("EMP-001", "Ana", "Ventas", "Entrada a Turno", hoy),
            ("EMP-001", "Ana", "Ventas", "Salida a Pausa", hoy),
            ("EMP-002", "Luis", "Soporte", "Entrada a Turno", hoy),
            ("EMP-003", "Eva", "Marketing", "Entrada a Turno", ayer),
        ]
        gestor = GestorFichajes(None)
        self.assertEqual(gestor.calcular_empleados_hoy(registros), 2)
        self.assertEqual(gestor.calcular_departamentos(registros), 2)


if __name__ == "__main__":
    unittest.main()
