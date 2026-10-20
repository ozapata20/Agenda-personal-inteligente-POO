import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config


class DatabaseConfigTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.env_file = self.directory / ".env"
        self.legacy_file = self.directory / "database.conf"
        self.paths = patch.multiple(
            config,
            ENV_FILE=self.env_file,
            LEGACY_CONFIG_FILE=self.legacy_file,
        )
        self.paths.start()
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.addCleanup(self.paths.stop)
        self.addCleanup(self.temp_dir.cleanup)

    def test_loads_dotenv_values(self):
        self.env_file.write_text(
            "DB_HOST=mysql.local\n"
            "DB_PORT=3307\n"
            "DB_NAME=agenda_test\n"
            "DB_USER=agenda_app\n"
            "DB_PASSWORD='clave segura'\n",
            encoding="utf-8",
        )

        settings = config.load_database_config()

        self.assertEqual(settings["host"], "mysql.local")
        self.assertEqual(settings["port"], 3307)
        self.assertEqual(settings["database"], "agenda_test")
        self.assertEqual(settings["user"], "agenda_app")
        self.assertEqual(settings["password"], "clave segura")
        self.assertEqual(settings["charset"], "utf8mb4")
        self.assertEqual(settings["connect_timeout"], 5)

    def test_environment_variables_override_dotenv(self):
        self.env_file.write_text(
            "DB_HOST=dotenv.local\n"
            "DB_NAME=agenda\n"
            "DB_USER=dotenv_user\n"
            "DB_PASSWORD=dotenv_password\n",
            encoding="utf-8",
        )
        os.environ["DB_HOST"] = "environment.local"

        settings = config.load_database_config()

        self.assertEqual(settings["host"], "environment.local")

    def test_falls_back_to_legacy_config(self):
        self.legacy_file.write_text(
            "[mysql]\n"
            "host = localhost\n"
            "database = agenda\n"
            "user = legacy_user\n"
            "password = legacy_password\n",
            encoding="utf-8",
        )

        settings = config.load_database_config()

        self.assertEqual(settings["user"], "legacy_user")
        self.assertEqual(settings["password"], "legacy_password")

    def test_requires_credentials_when_no_config_is_available(self):
        with self.assertRaisesRegex(ValueError, "DB_PASSWORD"):
            config.load_database_config()


if __name__ == "__main__":
    unittest.main()
