import unittest

from employee_status import ordenar_fichajes


class OrdenHistoricoTest(unittest.TestCase):
    def setUp(self):
        self.registros = [
            {"id_registro": 10, "nombre_completo": "Álvaro", "departamento": "Ventas",
             "fecha": "2026-10-02", "hora": "09:00:00"},
            {"id_registro": 2, "nombre_completo": "Beatriz", "departamento": "Administración",
             "fecha": "2026-09-30", "hora": "08:00:00"},
            {"id_registro": 3, "nombre_completo": "Ana", "departamento": "Operaciones",
             "fecha": "2026-10-02", "hora": "08:00:00"},
        ]

    def test_fecha_ordenada_por_dia_y_hora(self):
        self.assertEqual(
            [r["id_registro"] for r in ordenar_fichajes(self.registros, "fecha", True)],
            [10, 3, 2],
        )

    def test_numero_ordenado_como_numero(self):
        self.assertEqual(
            [r["id_registro"] for r in ordenar_fichajes(self.registros, "id_registro", False)],
            [2, 3, 10],
        )

    def test_nombre_ignora_tildes(self):
        self.assertEqual(
            [r["id_registro"] for r in ordenar_fichajes(self.registros, "nombre_completo", False)],
            [10, 3, 2],
        )


if __name__ == "__main__":
    unittest.main()
