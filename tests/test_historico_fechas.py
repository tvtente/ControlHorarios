import unittest
from datetime import date, datetime

from employee_status import filtrar_fichajes_por_fecha, interpretar_rango_fechas


class FechasHistoricoTest(unittest.TestCase):
    def test_rango_inclusivo_y_fechas_de_excel(self):
        registros = [
            {"fecha": "2026-10-01"},
            {"fecha": date(2026, 10, 2)},
            {"fecha": datetime(2026, 10, 3, 9, 0)},
            {"fecha": ""},
        ]
        desde, hasta = interpretar_rango_fechas("01/10/2026", "02/10/2026")
        self.assertEqual(filtrar_fichajes_por_fecha(registros, desde, hasta), registros[:2])
        self.assertEqual(filtrar_fichajes_por_fecha(registros, desde, None), registros[:3])
        self.assertIs(filtrar_fichajes_por_fecha(registros), registros)

    def test_fechas_invalidas_y_rango_invertido(self):
        for desde, hasta in (
            ("31/02/2026", ""),
            ("1/10/2026", ""),
            ("", "2026-10-01"),
            ("03/10/2026", "02/10/2026"),
        ):
            with self.subTest(desde=desde, hasta=hasta), self.assertRaises(ValueError):
                interpretar_rango_fechas(desde, hasta)


if __name__ == "__main__":
    unittest.main()
