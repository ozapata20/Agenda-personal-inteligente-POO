from models import Categorias, Contactos, PatronesRecurrencia, Usuarios
from services.common import delete_record, get_record
from validators import (
    optional_text,
    parse_date,
    required_text,
    validate_color,
    validate_email,
)


class CategoriaService:
    @staticmethod
    def crear(nombre: str, color_hex: str = "#16eed9"):
        return Categorias.create(
            nombre=required_text(nombre, "El nombre", 50),
            color_hex=validate_color(color_hex),
        )

    @staticmethod
    def listar():
        return list(Categorias.select().order_by(Categorias.nombre))

    @staticmethod
    def actualizar(categoria_id: int, nombre: str, color_hex: str):
        categoria = get_record(Categorias, categoria_id, "categoría")
        categoria.nombre = required_text(nombre, "El nombre", 50)
        categoria.color_hex = validate_color(color_hex)
        categoria.save()
        return categoria

    @staticmethod
    def eliminar(categoria_id: int):
        delete_record(Categorias, categoria_id, "categoría")


class ContactoService:
    @staticmethod
    def crear(
        usuario_id: int, nombre: str, email: str | None = None,
        telefono: str | None = None
    ):
        usuario = get_record(Usuarios, usuario_id, "usuario")
        return Contactos.create(
            id_usuario=usuario,
            nombre=required_text(nombre, "El nombre", 100),
            email=validate_email(email, required=False),
            telefono=optional_text(telefono, 20),
        )

    @staticmethod
    def listar(usuario_id: int | None = None):
        query = Contactos.select().order_by(Contactos.nombre)
        if usuario_id is not None:
            query = query.where(Contactos.id_usuario == usuario_id)
        return list(query)

    @staticmethod
    def actualizar(
        contacto_id: int, nombre: str, email: str | None, telefono: str | None
    ):
        contacto = get_record(Contactos, contacto_id, "contacto")
        contacto.nombre = required_text(nombre, "El nombre", 100)
        contacto.email = validate_email(email, required=False)
        contacto.telefono = optional_text(telefono, 20)
        contacto.save()
        return contacto

    @staticmethod
    def eliminar(contacto_id: int):
        delete_record(Contactos, contacto_id, "contacto")


class RecurrenciaService:
    @staticmethod
    def crear(
        tipo_recurrencia: str,
        intervalo: int = 1,
        dias_repeticion: str | None = None,
        fecha_limite_repeticion: str | None = None,
    ):
        if intervalo < 1:
            raise ValueError("El intervalo debe ser mayor que cero.")
        return PatronesRecurrencia.create(
            tipo_recurrencia=required_text(tipo_recurrencia, "El tipo", 50),
            intervalo=intervalo,
            dias_repeticion=optional_text(dias_repeticion, 100),
            fecha_limite_repeticion=parse_date(
                fecha_limite_repeticion, "Fecha límite"
            ),
        )

    @staticmethod
    def listar():
        return list(
            PatronesRecurrencia.select().order_by(PatronesRecurrencia.id_recurrencia)
        )

    @staticmethod
    def actualizar(
        recurrencia_id: int,
        tipo_recurrencia: str,
        intervalo: int,
        dias_repeticion: str | None,
        fecha_limite_repeticion: str | None,
    ):
        if intervalo < 1:
            raise ValueError("El intervalo debe ser mayor que cero.")
        recurrencia = get_record(PatronesRecurrencia, recurrencia_id, "recurrencia")
        recurrencia.tipo_recurrencia = required_text(tipo_recurrencia, "El tipo", 50)
        recurrencia.intervalo = intervalo
        recurrencia.dias_repeticion = optional_text(dias_repeticion, 100)
        recurrencia.fecha_limite_repeticion = parse_date(
            fecha_limite_repeticion, "Fecha límite"
        )
        recurrencia.save()
        return recurrencia

    @staticmethod
    def eliminar(recurrencia_id: int):
        delete_record(PatronesRecurrencia, recurrencia_id, "recurrencia")
