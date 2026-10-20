from getpass import getpass

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
        print("Opción inválida.")


def show_users():
    users = UsuarioService.listar()
    if not users:
        print("No hay usuarios registrados.")
        return
    for user in users:
        print(f"{user.id_usuario}. {user.nombre} | {user.email}")


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
            f"{contact.email or '-'} | {contact.telefono or '-'} "
            f"| usuario {contact.id_usuario_id}"
        )


def show_activities(agenda_id: int):
    activities = ActividadService.listar(agenda_id)
    if not activities:
        print("La agenda no tiene actividades.")
        return
    for activity in activities:
        extra = ""
        if activity.tipo_actividad == "Tarea":
            detail = ActividadService.obtener_detalle(activity.id_actividad)["subtipo"]
            extra = f" | avance {detail.porcentaje_avance or 0:.0f}%"
        elif activity.tipo_actividad == "Evento":
            detail = ActividadService.obtener_detalle(activity.id_actividad)["subtipo"]
            extra = f" | {detail.hora_inicio}-{detail.hora_fin}"
        print(
            f"{activity.id_actividad}. {activity.fecha} | {activity.tipo_actividad} | "
            f"{activity.titulo} | {activity.estado} | {activity.prioridad}{extra}"
        )


def select_agenda() -> int | None:
    agendas = UsuarioService.listar_agendas()
    if not agendas:
        print("Primero registra un usuario para crear su agenda.")
        return None
    for agenda in agendas:
        print(
            f"{agenda.id_agenda}. {agenda.id_usuario.nombre} "
            f"({agenda.id_usuario.email})"
        )
    agenda_id = ask_int("ID de agenda: ")
    if not any(agenda.id_agenda == agenda_id for agenda in agendas):
        print("No existe una agenda con ese ID.")
        return None
    return agenda_id


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
    if activity_type == "Tarea":
        data["fecha_vencimiento"] = input(
            "Fecha de vencimiento (AAAA-MM-DD, opcional): "
        ).strip() or None
    elif activity_type == "Evento":
        data["hora_inicio"] = input("Hora inicio (HH:MM): ")
        data["hora_fin"] = input("Hora término (HH:MM): ")
        data["ubicacion"] = input("Ubicación (opcional): ")
    else:
        data["enlace_reunion"] = input("Enlace de reunión (opcional): ")
    activity = ActividadService.crear(**data)
    print(f"Actividad creada con ID {activity.id_actividad}.")


def update_activity(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID de actividad a actualizar: ")
    detail = ActividadService.obtener_detalle(activity_id)
    activity = detail["actividad"]
    if activity.id_agenda_id != agenda_id:
        raise ValueError("La actividad no pertenece a la agenda seleccionada.")
    categoria = input(
        f"ID categoría [{activity.id_categoria_id or ''}] (vacío para quitar): "
    ).strip()
    recurrence = input(
        f"ID recurrencia [{activity.id_recurrencia_id or ''}] (vacío para quitar): "
    ).strip()
    data = {
        "actividad_id": activity_id,
        "titulo": input(f"Título [{activity.titulo}]: ").strip() or activity.titulo,
        "descripcion": input(
            f"Descripción [{activity.descripcion or ''}]: "
        ).strip() or activity.descripcion or "",
        "fecha": input(f"Fecha [{activity.fecha}]: ").strip() or str(activity.fecha),
        "prioridad": ask_choice("Prioridad", PRIORITIES),
        "estado": ask_choice("Estado", ACTIVITY_STATES),
        "categoria_id": int(categoria) if categoria else None,
        "recurrencia_id": int(recurrence) if recurrence else None,
    }
    if activity.tipo_actividad == "Tarea":
        data["fecha_vencimiento"] = input(
            f"Vencimiento [{detail['subtipo'].fecha_vencimiento or ''}]: "
        ).strip() or (
            str(detail["subtipo"].fecha_vencimiento)
            if detail["subtipo"].fecha_vencimiento else None
        )
    elif activity.tipo_actividad == "Evento":
        data["hora_inicio"] = input(
            f"Hora inicio [{detail['subtipo'].hora_inicio}]: "
        ).strip() or str(detail["subtipo"].hora_inicio)[:5]
        data["hora_fin"] = input(
            f"Hora término [{detail['subtipo'].hora_fin}]: "
        ).strip() or str(detail["subtipo"].hora_fin)[:5]
        data["ubicacion"] = input(
            f"Ubicación [{detail['subtipo'].ubicacion or ''}]: "
        ).strip() or detail["subtipo"].ubicacion or ""
    else:
        data["enlace_reunion"] = input(
            f"Enlace [{detail['subtipo'].enlace_reunion or ''}]: "
        ).strip() or detail["subtipo"].enlace_reunion or ""
    ActividadService.actualizar(**data)
    print("Actividad actualizada.")


def manage_activities():
    agenda_id = select_agenda()
    if agenda_id is None:
        return
    while True:
        print("\n--- Actividades de agenda ---")
        print("1. Listar  2. Crear  3. Ver detalle  4. Actualizar")
        print("5. Actualizar avance de tarea  6. Eliminar")
        print("7. Gestionar contactos de compromiso  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_activities(agenda_id)
        elif choice == "2":
            create_activity(agenda_id)
        elif choice == "3":
            show_activities(agenda_id)
            activity_id = ask_int("ID de actividad: ")
            detail = ActividadService.obtener_detalle(activity_id)
            activity, subtype = detail["actividad"], detail["subtipo"]
            if activity.id_agenda_id != agenda_id:
                raise ValueError("La actividad no pertenece a la agenda seleccionada.")
            print(
                f"{activity.titulo} | {activity.tipo_actividad} | {activity.fecha}\n"
                f"{activity.descripcion or '(sin descripción)'} | "
                f"{activity.estado} | {activity.prioridad}"
            )
            print(f"Detalle: {subtype.__data__ if subtype else '-'}")
            if activity.tipo_actividad == "Compromiso":
                for contact in ActividadService.listar_contactos(activity_id):
                    print(f"Contacto: {contact.nombre} (ID {contact.id_contacto})")
        elif choice == "4":
            update_activity(agenda_id)
        elif choice == "5":
            show_activities(agenda_id)
            task_id = ask_int("ID de tarea: ")
            task = ActividadService.actualizar_avance_tarea(
                task_id, float(input("Nuevo avance (0-100): "))
            )
            print(f"Avance actualizado a {task.porcentaje_avance:.0f}%.")
        elif choice == "6":
            show_activities(agenda_id)
            activity_id = ask_int("ID de actividad a eliminar: ")
            detail = ActividadService.obtener_detalle(activity_id)["actividad"]
            if detail.id_agenda_id != agenda_id:
                raise ValueError("La actividad no pertenece a la agenda seleccionada.")
            confirm = input(f"¿Eliminar '{detail.titulo}' y sus detalles? (s/N): ").lower()
            if confirm == "s":
                ActividadService.eliminar(activity_id)
                print("Actividad eliminada.")
        elif choice == "7":
            manage_commitment_contacts(agenda_id)
        else:
            print("Opción inválida.")


def manage_commitment_contacts(agenda_id: int):
    show_activities(agenda_id)
    activity_id = ask_int("ID del compromiso: ")
    activity = ActividadService.obtener_detalle(activity_id)["actividad"]
    if activity.id_agenda_id != agenda_id or activity.tipo_actividad != "Compromiso":
        raise ValueError("Selecciona un compromiso de la agenda.")
    print("Contactos vinculados:")
    for contact in ActividadService.listar_contactos(activity_id):
        print(f"{contact.id_contacto}. {contact.nombre}")
    print("1. Vincular contacto  2. Desvincular contacto")
    choice = input("Opción: ").strip()
    show_contacts(activity.id_agenda.id_usuario_id)
    contact_id = ask_int("ID de contacto: ")
    if choice == "1":
        ActividadService.vincular_contacto(activity_id, contact_id)
        print("Contacto vinculado.")
    elif choice == "2":
        ActividadService.desvincular_contacto(activity_id, contact_id)
        print("Contacto desvinculado.")
    else:
        print("Opción inválida.")


def manage_users():
    while True:
        print("\n--- Usuarios y agendas ---")
        print("1. Listar  2. Registrar  3. Actualizar  4. Eliminar  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_users()
        elif choice == "2":
            user, agenda = UsuarioService.crear(
                input("Nombre: "),
                input("Correo: "),
                getpass("Contraseña (mínimo 8 caracteres): "),
            )
            print(
                f"Usuario creado: {user.id_usuario}; "
                f"agenda asociada: {agenda.id_agenda}."
            )
        elif choice == "3":
            show_users()
            user_id = ask_int("ID de usuario: ")
            user = UsuarioService.obtener(user_id)
            nombre = input(f"Nombre [{user.nombre}]: ").strip() or user.nombre
            email = input(f"Correo [{user.email}]: ").strip() or user.email
            password = getpass("Nueva contraseña (vacío para conservarla): ") or None
            UsuarioService.actualizar(user_id, nombre, email, password)
            print("Usuario actualizado.")
        elif choice == "4":
            show_users()
            user_id = ask_int("ID de usuario a eliminar: ")
            confirm = input("Se eliminará también su agenda y datos. ¿Continuar? (s/N): ")
            if confirm.strip().lower() == "s":
                UsuarioService.eliminar(user_id)
                print("Usuario eliminado.")
        else:
            print("Opción inválida.")


def manage_categories():
    while True:
        print("\n--- Categorías ---")
        print("1. Listar  2. Crear  3. Actualizar  4. Eliminar  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_categories()
        elif choice == "2":
            category = CategoriaService.crear(
                input("Nombre: "),
                input("Color hexadecimal #RRGGBB [#16eed9]: ").strip() or "#16eed9",
            )
            print(f"Categoría creada con ID {category.id_categoria}.")
        elif choice == "3":
            show_categories()
            category_id = ask_int("ID de categoría: ")
            category = CategoriaService.actualizar(
                category_id, input("Nombre: "), input("Color #RRGGBB: ")
            )
            print(f"Categoría {category.nombre} actualizada.")
        elif choice == "4":
            show_categories()
            CategoriaService.eliminar(ask_int("ID de categoría a eliminar: "))
            print("Categoría eliminada; las actividades conservarán su información.")
        else:
            print("Opción inválida.")


def manage_contacts():
    while True:
        print("\n--- Contactos ---")
        print("1. Listar  2. Crear  3. Actualizar  4. Eliminar  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_contacts()
        elif choice == "2":
            show_users()
            contact = ContactoService.crear(
                ask_int("ID del usuario dueño: "),
                input("Nombre: "),
                input("Correo (opcional): "),
                input("Teléfono (opcional): "),
            )
            print(f"Contacto creado con ID {contact.id_contacto}.")
        elif choice == "3":
            show_contacts()
            contact_id = ask_int("ID de contacto: ")
            contact = ContactoService.actualizar(
                contact_id,
                input("Nombre: "),
                input("Correo (opcional): "),
                input("Teléfono (opcional): "),
            )
            print(f"Contacto {contact.nombre} actualizado.")
        elif choice == "4":
            show_contacts()
            ContactoService.eliminar(ask_int("ID de contacto a eliminar: "))
            print("Contacto eliminado.")
        else:
            print("Opción inválida.")


def manage_recurrences():
    while True:
        print("\n--- Recurrencias ---")
        print("1. Listar  2. Crear  3. Actualizar  4. Eliminar  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_recurrences()
        elif choice == "2":
            pattern = RecurrenciaService.crear(
                input("Tipo (Diaria/Semanal/Mensual): "),
                int(input("Intervalo (ej. cada 2 semanas): ")),
                input("Días (opcional, ej. lunes,miércoles): "),
                input("Fecha límite AAAA-MM-DD (opcional): "),
            )
            print(f"Recurrencia creada con ID {pattern.id_recurrencia}.")
        elif choice == "3":
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
        elif choice == "4":
            show_recurrences()
            RecurrenciaService.eliminar(ask_int("ID de recurrencia a eliminar: "))
            print("Recurrencia eliminada.")
        else:
            print("Opción inválida.")


def manage_reminders():
    while True:
        print("\n--- Recordatorios ---")
        print("1. Listar  2. Crear  3. Actualizar  4. Eliminar  0. Volver")
        choice = input("Opción: ").strip()
        if choice == "0":
            return
        if choice == "1":
            for reminder in RecordatorioService.listar():
                print(
                    f"{reminder.id_recordatorio}. Actividad {reminder.id_actividad_id} | "
                    f"{reminder.fecha_hora} | enviado={reminder.enviado} | "
                    f"{reminder.mensaje}"
                )
        elif choice == "2":
            show_users()
            agenda_id = select_agenda()
            if agenda_id is None:
                continue
            show_activities(agenda_id)
            activity_id = ask_int("ID de actividad: ")
            activity = ActividadService.obtener_detalle(activity_id)["actividad"]
            if activity.id_agenda_id != agenda_id:
                raise ValueError("La actividad no pertenece a la agenda seleccionada.")
            reminder = RecordatorioService.crear(
                activity_id,
                input("Fecha y hora AAAA-MM-DD HH:MM: "),
                input("Mensaje: "),
            )
            print(f"Recordatorio creado con ID {reminder.id_recordatorio}.")
        elif choice == "3":
            for reminder in RecordatorioService.listar():
                print(f"{reminder.id_recordatorio}. {reminder.fecha_hora} {reminder.mensaje}")
            reminder_id = ask_int("ID de recordatorio: ")
            reminder = RecordatorioService.actualizar(
                reminder_id,
                input("Fecha y hora AAAA-MM-DD HH:MM: "),
                input("Mensaje: "),
                input("¿Enviado? (s/N): ").strip().lower() == "s",
            )
            print(f"Recordatorio {reminder.id_recordatorio} actualizado.")
        elif choice == "4":
            for reminder in RecordatorioService.listar():
                print(f"{reminder.id_recordatorio}. {reminder.fecha_hora} {reminder.mensaje}")
            RecordatorioService.eliminar(ask_int("ID de recordatorio a eliminar: "))
            print("Recordatorio eliminado.")
        else:
            print("Opción inválida.")


def run_console():
    print("=== Sistema de Gestión de Agenda ===")
    DatabaseManager.connect()
    DatabaseManager.create_tables(MODELS)
    print("Conexión MySQL lista.")
    while True:
        print("\n1. Usuarios y agendas  2. Actividades  3. Categorías")
        print("4. Contactos  5. Recurrencias  6. Recordatorios  0. Salir")
        choice = input("Opción: ").strip()
        actions = {
            "1": manage_users,
            "2": manage_activities,
            "3": manage_categories,
            "4": manage_contacts,
            "5": manage_recurrences,
            "6": manage_reminders,
        }
        if choice == "0":
            print("Hasta luego.")
            return
        action = actions.get(choice)
        if action is None:
            print("Opción inválida.")
            continue
        try:
            action()
        except (ValueError, RuntimeError, PeeweeException) as exc:
            print(f"No se pudo completar la operación: {exc}")


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
