from peewee import IntegrityError

from models import Agendas, Usuarios
from security import hash_password, is_legacy_hash, verify_password
from services.common import atomic_for, delete_record, get_record
from services.validaciones import (
    validar_contrasenia,
    validar_correo,
    validar_rut,
)
from validators import required_text


def _hash_password(password: str) -> str:
    validated_password, errors = validar_contrasenia(password)
    if errors:
        raise ValueError("\n".join(errors))
    return hash_password(validated_password)


class UsuarioService:
    @staticmethod
    def crear(nombre: str, rut: str, email: str, password: str):
        nombre = required_text(nombre, "El nombre", 100)
        rut = required_text(rut, "El RUT", 12).upper()
        if not validar_rut(rut):
            raise ValueError("El RUT no es válido.")
        email, email_message = validar_correo(email.strip())
        if not email:
            raise ValueError(email_message)
        password_hash = _hash_password(password)
        try:
            with atomic_for(Usuarios):
                usuario = Usuarios.create(
                    nombre=nombre,
                    rut=rut,
                    email=email,
                    password_hash=password_hash,
                )
                agenda = Agendas.create(id_usuario=usuario)
                return usuario, agenda
        except IntegrityError as exc:
            if Usuarios.get_or_none(Usuarios.rut == rut):
                raise ValueError(
                    f"El RUT '{rut}' ya se encuentra registrado."
                ) from exc
            if Usuarios.get_or_none(Usuarios.email == email):
                raise ValueError(
                    f"El correo '{email}' ya se encuentra registrado."
                ) from exc
            raise ValueError(
                "No se pudo crear el usuario por un conflicto de integridad."
            ) from exc

    @staticmethod
    def autenticar(email: str, password: str):
        """Devuelve el usuario si las credenciales son correctas; si no, ValueError."""
        error = ValueError("Correo o contraseña incorrectos.")
        email, _ = validar_correo(email.strip())
        if not email:
            raise error from None
        usuario = Usuarios.get_or_none(Usuarios.email == email)
        stored_hash = usuario.password_hash if usuario else None
        if not verify_password(password, stored_hash):
            raise error
        # Migra hashes antiguos (PBKDF2) a bcrypt de forma transparente
        if is_legacy_hash(usuario.password_hash):
            usuario.password_hash = hash_password(password)
            usuario.save()
        return usuario

    @staticmethod
    def listar():
        return list(Usuarios.select().order_by(Usuarios.nombre))

    @staticmethod
    def obtener(usuario_id: int):
        return get_record(Usuarios, usuario_id, "usuario")

    @staticmethod
    def listar_agendas():
        return list(
            Agendas.select(Agendas, Usuarios)
            .join(Usuarios)
            .order_by(Agendas.id_agenda)
        )

    @staticmethod
    def actualizar(
        usuario_id: int, nombre: str, email: str, password: str | None = None
    ):
        usuario = get_record(Usuarios, usuario_id, "usuario")
        usuario.nombre = required_text(nombre, "El nombre", 100)
        usuario.email, email_message = validar_correo(email.strip())
        if not usuario.email:
            raise ValueError(email_message)
        if password:
            usuario.password_hash = _hash_password(password)
        try:
            usuario.save()
        except IntegrityError as exc:
            raise ValueError(
                f"El correo '{usuario.email}' ya se encuentra registrado."
            ) from exc
        return usuario

    @staticmethod
    def eliminar(usuario_id: int):
        delete_record(Usuarios, usuario_id, "usuario")