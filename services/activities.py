from peewee import IntegrityError

from models import (
    Actividades,
    Agendas,
    Categorias,
    CompromisoContacto,
    Compromisos,
    Contactos,
    Eventos,
    PatronesRecurrencia,
    Tareas,
)
from services.common import atomic_for, delete_record, get_record
from validators import (
    ACTIVITY_TYPES,
    parse_date,
    parse_time,
    required_text,
    validate_percentage,
    validate_priority,
    validate_state,
)


class ActividadService:
    @staticmethod
    def crear(
        agenda_id: int,
        titulo: str,
        tipo_actividad: str,
        fecha: str,
        descripcion: str = "",
        prioridad: str = "Media",
        categoria_id: int | None = None,
        recurrencia_id: int | None = None,
        fecha_vencimiento: str | None = None,
        hora_inicio: str | None = None,
        hora_fin: str | None = None,
        ubicacion: str | None = None,
        enlace_reunion: str | None = None,
    ):
        if tipo_actividad not in ACTIVITY_TYPES:
            raise ValueError(f"El tipo debe ser: {', '.join(ACTIVITY_TYPES)}.")
        agenda = get_record(Agendas, agenda_id, "agenda")
        categoria = (
            get_record(Categorias, categoria_id, "categoría")
            if categoria_id is not None else None
        )
        recurrencia = (
            get_record(PatronesRecurrencia, recurrencia_id, "recurrencia")
            if recurrencia_id is not None else None
        )
        titulo = required_text(titulo, "El título", 150)
        fecha_actividad = parse_date(fecha)
        prioridad = validate_priority(prioridad)

        evento_data = None
        if tipo_actividad == "Evento":
            inicio = parse_time(hora_inicio or "", "Hora de inicio")
            fin = parse_time(hora_fin or "", "Hora de término")
            if fin <= inicio:
                raise ValueError("La hora de término debe ser posterior a la de inicio.")
            evento_data = (inicio, fin, (ubicacion or "").strip() or None)
        fecha_venc = (
            parse_date(fecha_vencimiento, "Fecha de vencimiento")
            if tipo_actividad == "Tarea" else None
        )

        with atomic_for(Actividades):
            actividad = Actividades.create(
                id_agenda=agenda,
                id_categoria=categoria,
                id_recurrencia=recurrencia,
                titulo=titulo,
                descripcion=descripcion.strip() or None,
                fecha=fecha_actividad,
                tipo_actividad=tipo_actividad,
                prioridad=prioridad,
                estado="Pendiente",
            )
            if tipo_actividad == "Tarea":
                Tareas.create(id_actividad=actividad, fecha_vencimiento=fecha_venc)
            elif tipo_actividad == "Evento":
                Eventos.create(
                    id_actividad=actividad,
                    hora_inicio=evento_data[0],
                    hora_fin=evento_data[1],
                    ubicacion=evento_data[2],
                )
            else:
                Compromisos.create(
                    id_actividad=actividad,
                    enlace_reunion=(enlace_reunion or "").strip() or None,
                )
        return actividad

    @staticmethod
    def listar(agenda_id: int):
        get_record(Agendas, agenda_id, "agenda")
        return list(
            Actividades.select()
            .where(Actividades.id_agenda == agenda_id)
            .order_by(Actividades.fecha, Actividades.id_actividad)
        )

    @staticmethod
    def obtener_detalle(actividad_id: int):
        actividad = get_record(Actividades, actividad_id, "actividad")
        subtipo = None
        if actividad.tipo_actividad == "Tarea":
            subtipo = get_record(Tareas, actividad_id, "tarea")
        elif actividad.tipo_actividad == "Evento":
            subtipo = get_record(Eventos, actividad_id, "evento")
        elif actividad.tipo_actividad == "Compromiso":
            subtipo = get_record(Compromisos, actividad_id, "compromiso")
        return {"actividad": actividad, "subtipo": subtipo}

    @staticmethod
    def actualizar(
        actividad_id: int,
        titulo: str,
        descripcion: str,
        fecha: str,
        prioridad: str,
        estado: str,
        categoria_id: int | None,
        recurrencia_id: int | None,
        fecha_vencimiento: str | None = None,
        hora_inicio: str | None = None,
        hora_fin: str | None = None,
        ubicacion: str | None = None,
        enlace_reunion: str | None = None,
    ):
        actividad = get_record(Actividades, actividad_id, "actividad")
        categoria = (
            get_record(Categorias, categoria_id, "categoría")
            if categoria_id is not None else None
        )
        recurrencia = (
            get_record(PatronesRecurrencia, recurrencia_id, "recurrencia")
            if recurrencia_id is not None else None
        )
        actividad.titulo = required_text(titulo, "El título", 150)
        actividad.descripcion = descripcion.strip() or None
        actividad.fecha = parse_date(fecha)
        actividad.prioridad = validate_priority(prioridad)
        actividad.estado = validate_state(estado)
        actividad.id_categoria = categoria
        actividad.id_recurrencia = recurrencia

        with atomic_for(Actividades):
            actividad.save()
            if actividad.tipo_actividad == "Tarea":
                tarea = get_record(Tareas, actividad_id, "tarea")
                tarea.fecha_vencimiento = parse_date(
                    fecha_vencimiento, "Fecha de vencimiento"
                )
                tarea.save()
            elif actividad.tipo_actividad == "Evento":
                evento = get_record(Eventos, actividad_id, "evento")
                inicio = parse_time(hora_inicio or "", "Hora de inicio")
                fin = parse_time(hora_fin or "", "Hora de término")
                if fin <= inicio:
                    raise ValueError(
                        "La hora de término debe ser posterior a la de inicio."
                    )
                evento.hora_inicio = inicio
                evento.hora_fin = fin
                evento.ubicacion = (ubicacion or "").strip() or None
                evento.save()
            elif actividad.tipo_actividad == "Compromiso":
                compromiso = get_record(Compromisos, actividad_id, "compromiso")
                compromiso.enlace_reunion = (enlace_reunion or "").strip() or None
                compromiso.save()
        return actividad

    @staticmethod
    def actualizar_avance_tarea(actividad_id: int, porcentaje: float):
        progreso = validate_percentage(porcentaje)
        tarea = get_record(Tareas, actividad_id, "tarea")
        actividad = get_record(Actividades, actividad_id, "actividad")
        with atomic_for(Actividades):
            tarea.porcentaje_avance = progreso
            tarea.save()
            if progreso == 100:
                actividad.estado = "Completada"
            elif progreso == 0:
                actividad.estado = "Pendiente"
            else:
                actividad.estado = "En Proceso"
            actividad.save()
        return tarea

    @staticmethod
    def eliminar(actividad_id: int):
        delete_record(Actividades, actividad_id, "actividad")

    @staticmethod
    def vincular_contacto(actividad_id: int, contacto_id: int):
        actividad = get_record(Actividades, actividad_id, "actividad")
        if actividad.tipo_actividad != "Compromiso":
            raise ValueError("Solo se vinculan contactos a un compromiso.")
        compromiso = get_record(Compromisos, actividad_id, "compromiso")
        contacto = get_record(Contactos, contacto_id, "contacto")
        if contacto.id_usuario_id != actividad.id_agenda.id_usuario_id:
            raise ValueError("El contacto debe pertenecer al dueño de la agenda.")
        try:
            return CompromisoContacto.create(
                id_actividad=compromiso, id_contacto=contacto
            )
        except IntegrityError as exc:
            raise ValueError("Ese contacto ya está vinculado al compromiso.") from exc

    @staticmethod
    def listar_contactos(actividad_id: int):
        compromiso = get_record(Compromisos, actividad_id, "compromiso")
        query = (
            Contactos.select()
            .join(CompromisoContacto)
            .where(CompromisoContacto.id_actividad == compromiso)
            .order_by(Contactos.nombre)
        )
        return list(query)

    @staticmethod
    def desvincular_contacto(actividad_id: int, contacto_id: int):
        compromiso = get_record(Compromisos, actividad_id, "compromiso")
        contacto = get_record(Contactos, contacto_id, "contacto")
        deleted = (
            CompromisoContacto.delete()
            .where(
                (CompromisoContacto.id_actividad == compromiso)
                & (CompromisoContacto.id_contacto == contacto)
            )
            .execute()
        )
        if not deleted:
            raise ValueError("El contacto no estaba vinculado a ese compromiso.")
