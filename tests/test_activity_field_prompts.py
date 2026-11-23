import unittest
from unittest.mock import patch

from presentacion.app import CREATE_FIELDS


class ActivityFieldPromptsTest(unittest.TestCase):
    def test_activity_types_collect_fields_through_common_interface(self):
        cases = (
            ("Tarea", ["2026-12-01"], {"fecha_vencimiento": "2026-12-01"}),
            (
                "Evento",
                ["09:00", "10:00", "Oficina"],
                {
                    "hora_inicio": "09:00",
                    "hora_fin": "10:00",
                    "ubicacion": "Oficina",
                },
            ),
            (
                "Compromiso",
                ["https://example.cl"],
                {"enlace_reunion": "https://example.cl"},
            ),
        )

        for activity_type, answers, expected in cases:
            with self.subTest(activity_type=activity_type), patch(
                "builtins.input", side_effect=answers
            ):
                fields = CREATE_FIELDS[activity_type].collect()
            self.assertEqual(fields, expected)


if __name__ == "__main__":
    unittest.main()
