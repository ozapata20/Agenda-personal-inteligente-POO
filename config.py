import os
from configparser import ConfigParser
from pathlib import Path

from dotenv import dotenv_values

PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
LEGACY_CONFIG_FILE = PROJECT_DIR / "database.conf"
ENVIRONMENT_KEYS = {
    "host": "DB_HOST",
    "port": "DB_PORT",
    "database": "DB_NAME",
    "user": "DB_USER",
    "password": "DB_PASSWORD",
    "charset": "DB_CHARSET",
    "connect_timeout": "DB_CONNECT_TIMEOUT",
}


def load_database_config() -> dict[str, object]:
    env_values = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
    legacy_section = _load_legacy_config()

    def setting(name: str, default: str = "") -> str:
        value = os.getenv(ENVIRONMENT_KEYS[name])
        if value is None or not value.strip():
            value = env_values.get(ENVIRONMENT_KEYS[name])
        if value is None or not value.strip():
            value = legacy_section.get(name, default)
        return value.strip() if name != "password" else value

    required = ("host", "database", "user", "password")
    missing = [key for key in required if not setting(key).strip()]
    if missing:
        missing_variables = ", ".join(ENVIRONMENT_KEYS[key] for key in missing)
        raise ValueError(
            f"Faltan variables de configuración de MySQL: {missing_variables}. "
            f"Completa {ENV_FILE} usando .env.example."
        )

    try:
        port = int(setting("port", "3306"))
        connect_timeout = int(setting("connect_timeout", "5"))
    except ValueError as exc:
        raise ValueError("El puerto y connect_timeout deben ser números enteros.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("El puerto MySQL debe estar entre 1 y 65535.")
    if connect_timeout < 1:
        raise ValueError("connect_timeout debe ser mayor que cero.")

    return {
        "host": setting("host"),
        "port": port,
        "database": setting("database"),
        "user": setting("user"),
        "password": setting("password"),
        "charset": setting("charset", "utf8mb4"),
        "connect_timeout": connect_timeout,
    }


def _load_legacy_config() -> dict[str, str]:
    parser = ConfigParser()
    if LEGACY_CONFIG_FILE.exists():
        parser.read(LEGACY_CONFIG_FILE, encoding="utf-8")
    return dict(parser["mysql"]) if parser.has_section("mysql") else {}
