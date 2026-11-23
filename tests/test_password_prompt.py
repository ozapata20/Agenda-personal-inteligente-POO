import sys
import unittest
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from presentacion.app import read_password


class ReadPasswordTest(unittest.TestCase):
    def test_echoes_asterisks_and_supports_backspace(self):
        msvcrt = SimpleNamespace(
            getwch=Mock(side_effect=["a", "b", "\b", "c", "\r"])
        )
        output = StringIO()

        with patch.dict(sys.modules, {"msvcrt": msvcrt}), patch(
            "sys.stdout", output
        ):
            password = read_password("Contraseña: ")

        self.assertEqual(password, "ac")
        self.assertEqual(output.getvalue(), "Contraseña: **\b \b*\n")


if __name__ == "__main__":
    unittest.main()
