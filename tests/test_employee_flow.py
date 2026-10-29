import unittest
from datetime import datetime

from employee_status import siguiente_fichaje, validar_fichaje


class EmployeeFlowTests(unittest.TestCase):
    def setUp(self):
        self.ahora = datetime(2026, 10, 29, 18, 0)
        self.registros = []

    def agregar(self, accion, hora):
        self.registros.append({
            "id_empleado": "EMP-001",
            "accion": accion,
            "fecha": "2026-10-29",
            "hora": hora,
            "hora_inicio_prevista": "08:00",
            "hora_fin_prevista": "17:00",
        })

    def test_solo_se_permite_el_siguiente_paso(self):
        pasos = (
            ("Entrada a Turno", "08:00:00"),
            ("Inicio de Descanso", "12:00:00"),
            ("Fin de Descanso", "12:30:00"),
            ("Salida de Turno", "17:00:00"),
        )
        for accion, hora in pasos:
            self.assertEqual(siguiente_fichaje(self.registros, "EMP-001", ahora=self.ahora), accion)
            validar_fichaje(self.registros, "EMP-001", accion, ahora=self.ahora)
            self.agregar(accion, hora)
        self.assertIsNone(siguiente_fichaje(self.registros, "EMP-001", ahora=self.ahora))
        with self.assertRaisesRegex(ValueError, "ya terminó"):
            validar_fichaje(self.registros, "EMP-001", "Entrada a Turno", ahora=self.ahora)

    def test_no_se_puede_saltar_el_descanso(self):
        self.agregar("Entrada a Turno", "08:00:00")
        with self.assertRaisesRegex(ValueError, "Inicio de Descanso"):
            validar_fichaje(self.registros, "EMP-001", "Salida de Turno", ahora=self.ahora)

    def test_al_dia_siguiente_vuelve_a_permitirse_la_entrada(self):
        self.agregar("Salida de Turno", "17:00:00")
        manana = datetime(2026, 10, 30, 8, 0)
        self.assertEqual(siguiente_fichaje(self.registros, "EMP-001", ahora=manana), "Entrada a Turno")


if __name__ == "__main__":
    unittest.main()
