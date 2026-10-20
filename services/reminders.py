from models import Actividades, Recordatorios
from services.common import delete_record, get_record
from validators import parse_datetime, required_text


class RecordatorioService:
    @staticmethod
    def crear(actividad_id: int, fecha_hora: str, mensaje: str):
        actividad = get_record(Actividades, actividad_id, "actividad")
        return Recordatorios.create(
            id_actividad=actividad,
            fecha_hora=parse_datetime(fecha_hora),
            mensaje=required_text(mensaje, "El mensaje"),
            enviado=False,
        )

    @staticmethod
    def listar(actividad_id: int | None = None):
        query = Recordatorios.select().order_by(Recordatorios.fecha_hora)
        if actividad_id is not None:
            query = query.where(Recordatorios.id_actividad == actividad_id)
        return list(query)

    @staticmethod
    def actualizar(
        recordatorio_id: int, fecha_hora: str, mensaje: str, enviado: bool
    ):
        recordatorio = get_record(Recordatorios, recordatorio_id, "recordatorio")
        recordatorio.fecha_hora = parse_datetime(fecha_hora)
        recordatorio.mensaje = required_text(mensaje, "El mensaje")
        recordatorio.enviado = enviado
        recordatorio.save()
        return recordatorio

    @staticmethod
    def eliminar(recordatorio_id: int):
        delete_record(Recordatorios, recordatorio_id, "recordatorio")
