import re
from datetime import date, datetime, time


PRIORITIES = ("Baja", "Media", "Alta")
ACTIVITY_STATES = ("Pendiente", "En Proceso", "Completada", "Cancelada")
ACTIVITY_TYPES = ("Tarea", "Evento", "Compromiso")


def required_text(value: str, label: str, max_length: int | None = None) -> str:
    result = value.strip()
    if not result:
        raise ValueError(f"{label} es obligatorio.")
    if max_length is not None and len(result) > max_length:
        raise ValueError(f"{label} no puede superar {max_length} caracteres.")
    return result


def optional_text(value: str | None, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    result = value.strip()
    if not result:
        return None
    if max_length is not None and len(result) > max_length:
        raise ValueError(f"El texto no puede superar {max_length} caracteres.")
    return result


def validate_email(value: str | None, required: bool = True) -> str | None:
    email = optional_text(value, 150)
    if email is None:
        if required:
            raise ValueError("El correo electrónico es obligatorio.")
        return None
    if not re.fullmatch(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", email):
        raise ValueError("El formato del correo electrónico es inválido.")
    return email


def parse_date(value: str | date | None, label: str = "Fecha") -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{label}: use el formato AAAA-MM-DD.") from exc


def parse_time(value: str | time, label: str = "Hora") -> time:
    if isinstance(value, time):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"{label}: use el formato HH:MM.") from exc


def parse_datetime(value: str | datetime, label: str = "Fecha y hora") -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise ValueError(f"{label}: use el formato AAAA-MM-DD HH:MM.") from exc


def validate_priority(value: str) -> str:
    result = required_text(value, "La prioridad")
    if result not in PRIORITIES:
        raise ValueError(f"La prioridad debe ser: {', '.join(PRIORITIES)}.")
    return result


def validate_state(value: str) -> str:
    result = required_text(value, "El estado")
    if result not in ACTIVITY_STATES:
        raise ValueError(f"El estado debe ser: {', '.join(ACTIVITY_STATES)}.")
    return result


def validate_color(value: str) -> str:
    result = required_text(value, "El color")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", result):
        raise ValueError("El color debe tener formato hexadecimal #RRGGBB.")
    return result


def validate_percentage(value: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("El avance debe ser un número entre 0 y 100.") from exc
    if not 0 <= result <= 100:
        raise ValueError("El avance debe estar entre 0 y 100.")
    return result
