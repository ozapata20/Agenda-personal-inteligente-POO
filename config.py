from configparser import ConfigParser
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_DIR / "database.conf"


def load_database_config() -> dict[str, object]:
    parser = ConfigParser()
    if not parser.read(CONFIG_FILE, encoding="utf-8"):
        raise FileNotFoundError(
            f"No existe {CONFIG_FILE}. Copia database.example.conf como "
            "database.conf y completa la configuración de MySQL."
        )
    if not parser.has_section("mysql"):
        raise ValueError("El archivo database.conf debe incluir la sección [mysql].")

    section = parser["mysql"]
    required = ("host", "database", "user", "password")
    missing = [key for key in required if not section.get(key, "").strip()]
    if missing:
        raise ValueError(f"Faltan valores de configuración: {', '.join(missing)}.")

    port = section.getint("port", fallback=3306)
    if not 1 <= port <= 65535:
        raise ValueError("El puerto MySQL debe estar entre 1 y 65535.")

    return {
        "host": section["host"].strip(),
        "port": port,
        "database": section["database"].strip(),
        "user": section["user"].strip(),
        "password": section["password"],
        "charset": section.get("charset", "utf8mb4").strip(),
        "connect_timeout": section.getint("connect_timeout", fallback=5),
    }
