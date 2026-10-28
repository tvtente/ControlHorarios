import unittest
from datetime import date

from dashboard import build_dashboard_data


class DashboardDataTests(unittest.TestCase):
    def test_breaks_count_as_records_but_do_not_close_a_shift(self):
        records = [
            {"id_empleado": "A", "fecha": "2026-10-28", "hora": "09:00:00",
             "accion": "Entrada a Turno", "departamento": "Reservas"},
            {"id_empleado": "A", "fecha": "2026-10-28", "hora": "12:00:00",
             "accion": "Inicio de Descanso", "departamento": "Reservas"},
            {"id_empleado": "B", "fecha": "2026-10-28", "hora": "08:00:00",
             "accion": "Entrada a Turno", "departamento": "Operaciones"},
            {"id_empleado": "B", "fecha": "2026-10-28", "hora": "17:00:00",
             "accion": "Salida de Turno", "departamento": "Operaciones"},
        ]
        data = build_dashboard_data(records, hoy=date(2026, 10, 28))

        self.assertEqual((data["fichajes_hoy"], data["entradas_hoy"],
                          data["salidas_hoy"], data["jornadas_abiertas"]),
                         (4, 2, 1, 1))
        self.assertEqual(data["dias"][-1][1:], (2, 1))
        self.assertEqual(dict(data["departamentos"]),
                         {"Reservas": 2, "Operaciones": 2})

    def test_latest_shift_movement_wins_even_when_rows_are_unsorted(self):
        records = [
            {"id_empleado": "A", "fecha": "2026-10-28", "hora": "18:00:00",
             "accion": "Salida de Turno"},
            {"id_empleado": "A", "fecha": "2026-10-28", "hora": "09:00:00",
             "accion": "Entrada a Turno"},
        ]
        data = build_dashboard_data(records, hoy=date(2026, 10, 28))
        self.assertEqual(data["jornadas_abiertas"], 0)

    def test_empty_period_still_has_the_requested_days(self):
        data = build_dashboard_data([], hoy=date(2026, 10, 28), dias=14)
        self.assertEqual(len(data["dias"]), 14)
        self.assertEqual(data["dias"][-1], (date(2026, 10, 28), 0, 0))
        self.assertEqual(data["fichajes_hoy"], 0)


if __name__ == "__main__":
    unittest.main()
