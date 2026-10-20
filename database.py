from peewee import MySQLDatabase, PeeweeException

from config import load_database_config


database = MySQLDatabase(None)


class DatabaseManager:
    @staticmethod
    def connect():
        settings = load_database_config()
        database.init(
            settings["database"],
            host=settings["host"],
            port=settings["port"],
            user=settings["user"],
            password=settings["password"],
            charset=settings["charset"],
            connect_timeout=settings["connect_timeout"],
        )
        try:
            database.connect(reuse_if_open=True)
        except PeeweeException as exc:
            raise RuntimeError(
                f"No se pudo conectar a MySQL en {settings['host']}:{settings['port']} "
                f"con la base '{settings['database']}': {exc}"
            ) from exc
        return database

    @staticmethod
    def create_tables(models):
        try:
            database.create_tables(models, safe=True)
        except PeeweeException as exc:
            raise RuntimeError(f"No se pudieron preparar las tablas de agenda: {exc}") from exc

    @staticmethod
    def close():
        if not database.is_closed():
            database.close()
