import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from database import ensure_user_rut_column


class EnsureUserRutColumnTest(unittest.TestCase):
    def test_adds_nullable_unique_rut_when_missing(self):
        db = Mock()
        db.get_columns.return_value = [SimpleNamespace(name="id_usuario")]

        ensure_user_rut_column(db)

        db.execute_sql.assert_called_once_with(
            "ALTER TABLE `usuarios` ADD COLUMN `rut` VARCHAR(12) NULL UNIQUE"
        )

    def test_does_not_change_table_when_rut_exists(self):
        db = Mock()
        db.get_columns.return_value = [
            SimpleNamespace(name="id_usuario"),
            SimpleNamespace(name="rut"),
        ]

        ensure_user_rut_column(db)

        db.execute_sql.assert_not_called()


if __name__ == "__main__":
    unittest.main()
