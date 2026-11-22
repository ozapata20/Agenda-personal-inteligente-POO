from peewee import IntegrityError

from models import Agendas, Usuarios
from security import hash_password, is_legacy_hash, verify_password
from services.common import atomic_for, delete_record, get_record
from validators import required_text, validate_email


def _hash_password(password: str) -> str:
    if not password:
        raise ValueError("La contraseña es obligatoria.")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    return hash_password(password)


class UsuarioService:
    @staticmethod
    def crear(nombre: str, email: str, password: str):
        nombre = required_text(nombre, "El nombre", 100)
        email = validate_email(email)
        password_hash = _hash_password(password)
        try:
            with atomic_for(Usuarios):
                usuario = Usuarios.create(
                    nombre=nombre, email=email, password_hash=password_hash
                )
                agenda = Agendas.create(id_usuario=usuario)
                return usuario, agenda
        except IntegrityError as exc:
            raise ValueError(f"El correo '{email}' ya se encuentra registrado.") from exc

    @staticmethod
    def autenticar(email: str, password: str):
        """Devuelve el usuario si las credenciales son correctas; si no, ValueError."""
        error = ValueError("Correo o contraseña incorrectos.")
        try:
            email = validate_email(email)
        except ValueError:
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
        usuario.email = validate_email(email)
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