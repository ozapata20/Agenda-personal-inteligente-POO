from functools import partial
from getpass import getpass as hidden_getpass

from peewee import PeeweeException

from database import DatabaseManager
from models import MODELS
from services.activities import ActividadService
from services.catalog import (
    CategoriaService,
    ContactoService,
    RecurrenciaService,
)
from services.reminders import RecordatorioService
from services.users import UsuarioService
from validators import ACTIVITY_STATES, ACTIVITY_TYPES, PRIORITIES

# ---------------------------------------------------------------- Constantes
MAX_LOGIN_ATTEMPTS = 3

MSG_INVALID_OPTION = "Opción inválida."
MSG_BYE = "Hasta luego."
MSG_NOT_IN_AGENDA = "La actividad no pertenece a la agenda seleccionada."
MSG_NOT_YOUR_CONTACT = "Ese contacto no es tuyo."
MSG_NOT_YOUR_REMINDER = "Ese recordatorio no es tuyo."

PROMPT_OPTION = "Opción: "
PROMPT_NAME = "Nombre: "
PROMPT_EMAIL_OPT = "Correo (opcional): "
PROMPT_PHONE_OPT = "Teléfono (opcional): "
PROMPT_DATETIME = "Fecha y hora AAAA-MM-DD HH:MM: "
PROMPT_MESSAGE = "Mensaje: "
PROMPT_PASSWORD_NEW = (
    "Contraseña (8+ caracteres, mayúscula, minúscula, número y @ $ # ! * &): "
)

MENU_CRUD = "1. Listar  2. Crear  3. Actualizar  4. Eliminar  0. Volver"

CURRENT_USER = None  # se asigna tras el login


# ---------------------------------------------------------------- Utilidades
def read_password(prompt: str) -> str:
    try:
        import msvcrt
    except ImportError:
        return hidden_getpass(prompt)

    print(prompt, end="", flush=True)
    password: list[str] = []
    while True:
        char = msvcrt.getwch()
        if char in ("\r", "\n"):
            print()
            return "".join(password)
        if char == "\x03":
            raise KeyboardInterrupt
        if char == "\x1a":
            raise EOFError
        if char == "\b":
            if password:
                password.pop()
                print("\b \b", end="", flush=True)
            continue
        if char in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue
        password.append(char)
        print("*", end="", flush=True)


def ask_int(prompt: str, optional: bool = False) -> int | None:
    while True:
        value = input(prompt).strip()
        if optional and not value:
            return None
        try:
            result = int(value)
            if result <= 0:
                raise ValueError
            return result
        except ValueError:
            print("Ingresa un número entero positivo.")


def ask_choice(prompt: str, options: tuple[str, ...]) -> str:
    while True:
        value = input(f"{prompt} ({'/'.join(options)}): ").strip()
        if value in options:
            return value
        print(MSG_INVALID_OPTION)


def ask_default(label: str, current) -> str | None:
    """Pide un valor mostrando el actual; vacío conserva el actual."""
    value = input(f"{label} [{current or ''}]: ").strip()
    return value or current


def run_menu(title: str, lines: tuple[str, ...], handlers: dict) -> None:
    """Ejecuta un submenú. '0' vuelve; si un handler devuelve True, también sale."""
    while True:
        print(f"\n--- {title} ---")
        for line in lines:
            print(line)
        choice = input(PROMPT_OPTION).strip()
        if choice == "0":
            return
        handler = handlers.get(choice)
        if handler is None:
            print(MSG_INVALID_OPTION)
            continue
        if handler() is True:
            return


# ---------------------------------------------------------------- Autenticación
def login():
    """Pide credenciales. Devuelve el usuario autenticado o None."""
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        email = input("Correo: ").strip()
        password = read_password("Contraseña: ")
        try:
            user = UsuarioService.autenticar(email, password)
            print(f"Bienvenido, {user.nombre}.")
            return user
        except ValueError as exc:
            print(f"{exc} (intento {attempt}/{MAX_LOGIN_ATTEMPTS})")
    print("Demasiados intentos fallidos.")
    return None


def register():
    user, _agenda = UsuarioService.crear(
        input(PROMPT_NAME),
        input("RUT (ejemplo: 12.345.678-5): "),
        input("Correo: "),
        read_password(PROMPT_PASSWORD_NEW),
    )
    print(f"Usuario creado (ID {user.id_usuario}). Ya puedes iniciar sesión.")


def _auth_choice(choice: str):
    """Procesa una opción del menú de acceso. Devuelve el usuario si inicia sesión."""
    if choice == "1":
        return login()
    if choice == "2":
        register()
    else:
        print(MSG_INVALID_OPTION)
    return None


def auth_menu():
    """Menú previo al sistema. Devuelve el usuario logueado o None si sale."""
    while True:
        print("\n1. Iniciar sesión  2. Registrarse  0. Salir")
        choice = input(PROMPT_OPTION).strip()
        if choice == "0":
            return None
        try:
            user = _auth_choice(choice)
        except (ValueError, RuntimeError, PeeweeException) as exc:
            print(f"No se pudo completar la operación: {exc}")
            continue
        if user:
            return user


# ---------------------------------------------------------------- Listados
def show_categories():
    categories = CategoriaService.listar()
    if not categories:
        print("No hay categorías registradas.")
        return
    for category in categories:
        print(f"{category.id_categoria}. {category.nombre} | {category.color_hex}")


def show_recurrences():
    patterns = RecurrenciaService.listar()
    if not patterns:
        print("No hay patrones de recurrencia registrados.")
        return
    for pattern in patterns:
        print(
            f"{pattern.id_recurrencia}. {pattern.tipo_recurrencia} | "
            f"cada {pattern.intervalo} | días: {pattern.dias_repeticion or '-'}"
        )


def show_contacts(user_id: int | None = None):
    contacts = ContactoService.listar(user_id)
    if not contacts:
        print("No hay contactos registrados.")
        return
    for contact in contacts:
        print(
            f"{contact.id_contacto}. {contact.nombre} | "
            f"{contact.email or '-'} | {contact.telefono or '-'}"
        )


def _activity_extra(activity) -> str:
    if activity.tipo_actividad == "Tarea":
        detail = ActividadService.obtener_detalle(activity.id_actividad)["subtipo"]
        return f" | avance {detail.porcentaje_avance or 0:.0f}%"
    if activity.tipo_actividad == "Evento":
        detail = ActividadService.obtener_detalle(activity.id_actividad)["subtipo"]
        return f" | {detail.hora_inicio}-{detail.hora_fin}"
    return ""


def show_activities(agenda_id: int):
    activities = ActividadService.listar(agenda_id)
    if not activities:
        print("La agenda no tiene actividades.")
        return
    for activity in activities:
        print(
            f"{activity.id_actividad}. {activity.fecha} | {activity.tipo_actividad} | "
            f"{activity.titulo} | {activity.estado} | {activity.prioridad}"
            f"{_activity_extra(activity)}"
        )


def select_agenda() -> int | None:
    """Devuelve la agenda del usuario con sesión iniciada."""
    agendas = UsuarioService.listar_agendas()
    mine = next(
        (a for a in agendas if a.id_usuario_id == CURRENT_USER.id_usuario), None
    )
    if mine is None:
        print("Tu usuario no tiene agenda asociada.")
        return None
    return mine.id_agenda


# ---------------------------------------------------------------- Actividades
def get_own_activity(agenda_id: int, activity_id: int) -> dict:
    """Devuelve el detalle de la actividad si pertenece a la agenda; si no, ValueError."""
    detail = ActividadService.obtener_detalle(activity_id)
    if detail["actividad"].id_agenda_id != agenda_id:
        raise ValueError(MSG_NOT_IN_AGENDA)
    return detail


def _create_task_fields() -> dict:
    return {
        "fecha_vencimiento": input(
            "Fecha de vencimiento (AAAA-MM-DD, opcional): "
        ).strip() or None
    }


def _create_event_fields() -> dict:
    return {
        "hora_inicio": input("Hora inicio (HH:MM): "),
        "hora_fin": input("Hora término (HH:MM): "),
        "ubicacion": input("Ubicación (opcional): "),
    }


def _create_commitment_fields() -> dict:
    return {"enlace_reunion": input("Enlace de reunión (opcional): ")}


CREATE_FIELDS = {
    "Tarea": _create_task_fields,
    "Evento": _create_event_fields,
    "Compromiso": _create_commitment_fields,
}


def create_activity(agenda_id: int):
    print("Tipos: Tarea, Evento, Compromiso.")
    activity_type = ask_choice("Tipo", ACTIVITY_TYPES)
    show_categories()
    show_recurrences()
    category_id = ask_int("ID de categoría (vacío si ninguna): ", optional=True)
    recurrence_id = ask_int("ID de recurrencia (vacío si ninguna): ", optional=True)
    data = {
        "agenda_id": agenda_id,
        "titulo": input("Título: "),
        "tipo_actividad": activity_type,
        "fecha": input("Fecha (AAAA-MM-DD): "),
        "descripcion": input("Descripción (opcional): "),
        "prioridad": ask_choice("Prioridad", PRIORITIES),
        "categoria_id": category_id,
        "recurrencia_id": recurrence_id,
    }
    data.update(CREATE_FIELDS[activity_type]())
    activity = ActividadService.crear(**data)
    print(f"Actividad creada con ID {activity.id_actividad}.")


def _update_task_fields(sub) -> dict:
    current = str(sub.fecha_vencimiento) if sub.fecha_vencimiento else None
    return {"fecha_vencimiento": ask_default("Vencimiento", current)}


def _update_event_fields(sub) -> dict:
    return {
        "hora_inicio": ask_default("Hora inicio", str(sub.hora_inicio)[:5]),
        "hora_fin": ask_default("Hora término", str(sub.hora_fin)[:5]),
        "ubicacion": ask_default("Ubicación", sub.ubicacion or ""),
    }


def _update_commitment_fields(sub) -> dict:
    return {"enlace_reunion": ask_default("Enlace", sub.enlace_reunion or "")}


UPDATE_FIELDS = {
    "Tarea": _update_task_fields,
    "Evento": _update_event_fields,
    "Compromiso": _update_commitment_fields,
}


def _optional_id(label: str, current) -> int | None:
    value = input(f"{label} [{current or ''}] (vacío para quitar): ").strip()
    return int(value) if value else None


def update_activity(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID de actividad a actualizar: ")
    detail = get_own_activity(agenda_id, activity_id)
    activity, subtype = detail["actividad"], detail["subtipo"]
    data = {
        "actividad_id": activity_id,
        "categoria_id": _optional_id("ID categoría", activity.id_categoria_id),
        "recurrencia_id": _optional_id("ID recurrencia", activity.id_recurrencia_id),
        "titulo": ask_default("Título", activity.titulo),
        "descripcion": ask_default("Descripción", activity.descripcion or ""),
        "fecha": ask_default("Fecha", str(activity.fecha)),
        "prioridad": ask_choice("Prioridad", PRIORITIES),
        "estado": ask_choice("Estado", ACTIVITY_STATES),
    }
    data.update(UPDATE_FIELDS[activity.tipo_actividad](subtype))
    ActividadService.actualizar(**data)
    print("Actividad actualizada.")


def view_activity(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID de actividad: ")
    detail = get_own_activity(agenda_id, activity_id)
    activity, subtype = detail["actividad"], detail["subtipo"]
    print(
        f"{activity.titulo} | {activity.tipo_actividad} | {activity.fecha}\n"
        f"{activity.descripcion or '(sin descripción)'} | "
        f"{activity.estado} | {activity.prioridad}"
    )
    print(f"Detalle: {subtype.__data__ if subtype else '-'}")
    if activity.tipo_actividad == "Compromiso":
        for contact in ActividadService.listar_contactos(activity_id):
            print(f"Contacto: {contact.nombre} (ID {contact.id_contacto})")


def update_task_progress(agenda_id: int):
    show_activities(agenda_id)
    task_id = ask_int("ID de tarea: ")
    get_own_activity(agenda_id, task_id)
    task = ActividadService.actualizar_avance_tarea(
        task_id, float(input("Nuevo avance (0-100): "))
    )
    print(f"Avance actualizado a {task.porcentaje_avance:.0f}%.")


def delete_activity(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID de actividad a eliminar: ")
    activity = get_own_activity(agenda_id, activity_id)["actividad"]
    confirm = input(f"¿Eliminar '{activity.titulo}' y sus detalles? (s/N): ").lower()
    if confirm == "s":
        ActividadService.eliminar(activity_id)
        print("Actividad eliminada.")


def manage_commitment_contacts(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID del compromiso: ")
    activity = get_own_activity(agenda_id, activity_id)["actividad"]
    if activity.tipo_actividad != "Compromiso":
        raise ValueError("Selecciona un compromiso de la agenda.")
    print("Contactos vinculados:")
    for contact in ActividadService.listar_contactos(activity_id):
        print(f"{contact.id_contacto}. {contact.nombre}")
    print("1. Vincular contacto  2. Desvincular contacto")
    choice = input(PROMPT_OPTION).strip()
    show_contacts(CURRENT_USER.id_usuario)
    contact_id = ask_int("ID de contacto: ")
    if contact_id not in own_contact_ids():
        raise ValueError(MSG_NOT_YOUR_CONTACT)
    if choice == "1":
        ActividadService.vincular_contacto(activity_id, contact_id)
        print("Contacto vinculado.")
    elif choice == "2":
        ActividadService.desvincular_contacto(activity_id, contact_id)
        print("Contacto desvinculado.")
    else:
        print(MSG_INVALID_OPTION)


def manage_activities():
    agenda_id = select_agenda()
    if agenda_id is None:
        return
    run_menu(
        "Actividades de agenda",
        (
            "1. Listar  2. Crear  3. Ver detalle  4. Actualizar",
            "5. Actualizar avance de tarea  6. Eliminar",
            "7. Gestionar contactos de compromiso  0. Volver",
        ),
        {
            "1": partial(show_activities, agenda_id),
            "2": partial(create_activity, agenda_id),
            "3": partial(view_activity, agenda_id),
            "4": partial(update_activity, agenda_id),
            "5": partial(update_task_progress, agenda_id),
            "6": partial(delete_activity, agenda_id),
            "7": partial(manage_commitment_contacts, agenda_id),
        },
    )


# ---------------------------------------------------------------- Mi cuenta
def show_profile():
    print(f"{CURRENT_USER.nombre} | {CURRENT_USER.email}")


def update_profile():
    global CURRENT_USER
    user = UsuarioService.obtener(CURRENT_USER.id_usuario)
    nombre = ask_default("Nombre", user.nombre)
    email = ask_default("Correo", user.email)
    password = read_password("Nueva contraseña (vacío para conservarla): ") or None
    CURRENT_USER = UsuarioService.actualizar(user.id_usuario, nombre, email, password)
    print("Usuario actualizado.")


def delete_account() -> bool:
    """Elimina la cuenta propia. Devuelve True si se eliminó."""
    global CURRENT_USER
    confirm = input("Se eliminará tu cuenta, agenda y datos. ¿Continuar? (s/N): ")
    if confirm.strip().lower() != "s":
        return False
    # Reautenticación antes de una acción destructiva
    UsuarioService.autenticar(
        CURRENT_USER.email, read_password("Confirma tu contraseña: ")
    )
    UsuarioService.eliminar(CURRENT_USER.id_usuario)
    print("Cuenta eliminada.")
    CURRENT_USER = None
    return True


def manage_users():
    """Gestión de la cuenta propia (cada usuario solo ve y edita la suya)."""
    run_menu(
        "Mi cuenta",
        ("1. Ver perfil  2. Actualizar mis datos  3. Eliminar mi cuenta  0. Volver",),
        {"1": show_profile, "2": update_profile, "3": delete_account},
    )


# ---------------------------------------------------------------- Categorías
def create_category():
    category = CategoriaService.crear(
        input(PROMPT_NAME),
        input("Color hexadecimal #RRGGBB [#16eed9]: ").strip() or "#16eed9",
    )
    print(f"Categoría creada con ID {category.id_categoria}.")


def update_category():
    show_categories()
    category_id = ask_int("ID de categoría: ")
    category = CategoriaService.actualizar(
        category_id, input(PROMPT_NAME), input("Color #RRGGBB: ")
    )
    print(f"Categoría {category.nombre} actualizada.")


def delete_category():
    show_categories()
    CategoriaService.eliminar(ask_int("ID de categoría a eliminar: "))
    print("Categoría eliminada; las actividades conservarán su información.")


def manage_categories():
    run_menu(
        "Categorías",
        (MENU_CRUD,),
        {
            "1": show_categories,
            "2": create_category,
            "3": update_category,
            "4": delete_category,
        },
    )


# ---------------------------------------------------------------- Contactos
def own_contact_ids() -> set[int]:
    return {c.id_contacto for c in ContactoService.listar(CURRENT_USER.id_usuario)}


def _pick_own_contact(prompt: str) -> int:
    show_contacts(CURRENT_USER.id_usuario)
    contact_id = ask_int(prompt)
    if contact_id not in own_contact_ids():
        raise ValueError(MSG_NOT_YOUR_CONTACT)
    return contact_id


def list_contacts():
    show_contacts(CURRENT_USER.id_usuario)


def create_contact():
    contact = ContactoService.crear(
        CURRENT_USER.id_usuario,
        input(PROMPT_NAME),
        input(PROMPT_EMAIL_OPT),
        input(PROMPT_PHONE_OPT),
    )
    print(f"Contacto creado con ID {contact.id_contacto}.")


def update_contact():
    contact_id = _pick_own_contact("ID de contacto: ")
    contact = ContactoService.actualizar(
        contact_id,
        input(PROMPT_NAME),
        input(PROMPT_EMAIL_OPT),
        input(PROMPT_PHONE_OPT),
    )
    print(f"Contacto {contact.nombre} actualizado.")


def delete_contact():
    contact_id = _pick_own_contact("ID de contacto a eliminar: ")
    ContactoService.eliminar(contact_id)
    print("Contacto eliminado.")


def manage_contacts():
    run_menu(
        "Contactos",
        (MENU_CRUD,),
        {
            "1": list_contacts,
            "2": create_contact,
            "3": update_contact,
            "4": delete_contact,
        },
    )


# ---------------------------------------------------------------- Recurrencias
def create_recurrence():
    pattern = RecurrenciaService.crear(
        input("Tipo (Diaria/Semanal/Mensual): "),
        int(input("Intervalo (ej. cada 2 semanas): ")),
        input("Días (opcional, ej. lunes,miércoles): "),
        input("Fecha límite AAAA-MM-DD (opcional): "),
    )
    print(f"Recurrencia creada con ID {pattern.id_recurrencia}.")


def update_recurrence():
    show_recurrences()
    pattern_id = ask_int("ID de recurrencia: ")
    pattern = RecurrenciaService.actualizar(
        pattern_id,
        input("Tipo: "),
        int(input("Intervalo: ")),
        input("Días (opcional): "),
        input("Fecha límite AAAA-MM-DD (opcional): "),
    )
    print(f"Recurrencia {pattern.id_recurrencia} actualizada.")


def delete_recurrence():
    show_recurrences()
    RecurrenciaService.eliminar(ask_int("ID de recurrencia a eliminar: "))
    print("Recurrencia eliminada.")


def manage_recurrences():
    run_menu(
        "Recurrencias",
        (MENU_CRUD,),
        {
            "1": show_recurrences,
            "2": create_recurrence,
            "3": update_recurrence,
            "4": delete_recurrence,
        },
    )


# ---------------------------------------------------------------- Recordatorios
def own_reminders(agenda_id: int) -> list:
    """Recordatorios de las actividades de la agenda del usuario."""
    activity_ids = {a.id_actividad for a in ActividadService.listar(agenda_id)}
    return [
        r for r in RecordatorioService.listar() if r.id_actividad_id in activity_ids
    ]


def show_reminders(reminders: list):
    if not reminders:
        print("No tienes recordatorios.")
        return
    for reminder in reminders:
        print(
            f"{reminder.id_recordatorio}. Actividad {reminder.id_actividad_id} | "
            f"{reminder.fecha_hora} | enviado={reminder.enviado} | "
            f"{reminder.mensaje}"
        )


def _pick_own_reminder(agenda_id: int, prompt: str) -> int:
    mine = own_reminders(agenda_id)
    show_reminders(mine)
    reminder_id = ask_int(prompt)
    if reminder_id not in {r.id_recordatorio for r in mine}:
        raise ValueError(MSG_NOT_YOUR_REMINDER)
    return reminder_id


def list_reminders(agenda_id: int):
    show_reminders(own_reminders(agenda_id))


def create_reminder(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID de actividad: ")
    get_own_activity(agenda_id, activity_id)
    reminder = RecordatorioService.crear(
        activity_id, input(PROMPT_DATETIME), input(PROMPT_MESSAGE)
    )
    print(f"Recordatorio creado con ID {reminder.id_recordatorio}.")


def update_reminder(agenda_id: int):
    reminder_id = _pick_own_reminder(agenda_id, "ID de recordatorio: ")
    reminder = RecordatorioService.actualizar(
        reminder_id,
        input(PROMPT_DATETIME),
        input(PROMPT_MESSAGE),
        input("¿Enviado? (s/N): ").strip().lower() == "s",
    )
    print(f"Recordatorio {reminder.id_recordatorio} actualizado.")


def delete_reminder(agenda_id: int):
    reminder_id = _pick_own_reminder(agenda_id, "ID de recordatorio a eliminar: ")
    RecordatorioService.eliminar(reminder_id)
    print("Recordatorio eliminado.")


def manage_reminders():
    agenda_id = select_agenda()
    if agenda_id is None:
        return
    run_menu(
        "Recordatorios",
        (MENU_CRUD,),
        {
            "1": partial(list_reminders, agenda_id),
            "2": partial(create_reminder, agenda_id),
            "3": partial(update_reminder, agenda_id),
            "4": partial(delete_reminder, agenda_id),
        },
    )


# ---------------------------------------------------------------- Programa
ACTIONS = {
    "1": manage_users,
    "2": manage_activities,
    "3": manage_categories,
    "4": manage_contacts,
    "5": manage_recurrences,
    "6": manage_reminders,
}


def switch_session() -> bool:
    """Abre el menú de acceso. Devuelve False si el usuario decide salir."""
    global CURRENT_USER
    CURRENT_USER = auth_menu()
    if CURRENT_USER is None:
        print(MSG_BYE)
        return False
    return True


def run_action(choice: str) -> None:
    action = ACTIONS.get(choice)
    if action is None:
        print(MSG_INVALID_OPTION)
        return
    try:
        action()
    except (ValueError, RuntimeError, PeeweeException) as exc:
        print(f"No se pudo completar la operación: {exc}")


def run_console():
    print("=== Sistema de Gestión de Agenda ===")
    DatabaseManager.connect()
    DatabaseManager.create_tables(MODELS)
    print("Conexión MySQL lista.")

    if not switch_session():
        return

    while True:
        print(f"\n[Sesión: {CURRENT_USER.email}]")
        print("1. Mi cuenta  2. Actividades  3. Categorías")
        print("4. Contactos  5. Recurrencias  6. Recordatorios")
        print("9. Cerrar sesión  0. Salir")
        choice = input(PROMPT_OPTION).strip()
        if choice == "0":
            print(MSG_BYE)
            return
        if choice == "9":
            if not switch_session():
                return
            continue
        run_action(choice)
        # Si la cuenta fue eliminada, vuelve al menú de acceso
        if CURRENT_USER is None and not switch_session():
            return


def main():
    try:
        run_console()
    except (FileNotFoundError, ValueError, RuntimeError, PeeweeException) as exc:
        print(f"Error de configuración o base de datos: {exc}")
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        print("\nEjecución interrumpida.")
    finally:
        DatabaseManager.close()


if __name__ == "__main__":
    main()