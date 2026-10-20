from datetime import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    CompositeKey,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
    TimeField,
)

from database import database


class BaseModel(Model):
    class Meta:
        database = database


class Usuarios(BaseModel):
    id_usuario = AutoField()
    nombre = CharField(max_length=100)
    email = CharField(max_length=150, unique=True)
    password_hash = CharField()
    fecha_registro = DateTimeField(default=datetime.now, null=True)

    class Meta:
        table_name = "usuarios"


class Agendas(BaseModel):
    id_agenda = AutoField()
    id_usuario = ForeignKeyField(
        Usuarios,
        column_name="id_usuario",
        backref="agendas",
        on_delete="CASCADE",
        unique=True,
    )
    fecha_creacion = DateTimeField(default=datetime.now, null=True)

    class Meta:
        table_name = "agendas"


class Categorias(BaseModel):
    id_categoria = AutoField()
    nombre = CharField(max_length=50)
    color_hex = CharField(max_length=7, default="#16eed9", null=True)

    class Meta:
        table_name = "categorias"


class PatronesRecurrencia(BaseModel):
    id_recurrencia = AutoField()
    tipo_recurrencia = CharField(max_length=50)
    intervalo = IntegerField(default=1, null=True)
    dias_repeticion = CharField(max_length=100, null=True)
    fecha_limite_repeticion = DateField(null=True)

    class Meta:
        table_name = "patrones_recurrencia"


class Actividades(BaseModel):
    id_actividad = AutoField()
    id_agenda = ForeignKeyField(
        Agendas, column_name="id_agenda", backref="actividades", on_delete="CASCADE"
    )
    id_categoria = ForeignKeyField(
        Categorias,
        column_name="id_categoria",
        backref="actividades",
        null=True,
        on_delete="SET NULL",
    )
    id_recurrencia = ForeignKeyField(
        PatronesRecurrencia,
        column_name="id_recurrencia",
        backref="actividades",
        null=True,
        on_delete="SET NULL",
    )
    titulo = CharField(max_length=150)
    descripcion = TextField(null=True)
    fecha = DateField()
    tipo_actividad = CharField()
    prioridad = CharField(default="Media", null=True)
    estado = CharField(default="Pendiente", null=True)

    class Meta:
        table_name = "actividades"


class Tareas(BaseModel):
    id_actividad = ForeignKeyField(
        Actividades,
        column_name="id_actividad",
        backref="tarea",
        primary_key=True,
        on_delete="CASCADE",
    )
    fecha_vencimiento = DateField(null=True)
    porcentaje_avance = FloatField(default=0.0, null=True)

    class Meta:
        table_name = "tareas"


class Eventos(BaseModel):
    id_actividad = ForeignKeyField(
        Actividades,
        column_name="id_actividad",
        backref="evento",
        primary_key=True,
        on_delete="CASCADE",
    )
    hora_inicio = TimeField()
    hora_fin = TimeField()
    ubicacion = CharField(null=True)

    class Meta:
        table_name = "eventos"


class Compromisos(BaseModel):
    id_actividad = ForeignKeyField(
        Actividades,
        column_name="id_actividad",
        backref="compromiso",
        primary_key=True,
        on_delete="CASCADE",
    )
    enlace_reunion = CharField(null=True)

    class Meta:
        table_name = "compromisos"


class Contactos(BaseModel):
    id_contacto = AutoField()
    id_usuario = ForeignKeyField(
        Usuarios, column_name="id_usuario", backref="contactos", on_delete="CASCADE"
    )
    nombre = CharField(max_length=100)
    email = CharField(max_length=150, null=True)
    telefono = CharField(max_length=20, null=True)

    class Meta:
        table_name = "contactos"


class CompromisoContacto(BaseModel):
    id_actividad = ForeignKeyField(
        Compromisos, column_name="id_actividad", backref="contactos", on_delete="CASCADE"
    )
    id_contacto = ForeignKeyField(
        Contactos, column_name="id_contacto", backref="compromisos", on_delete="CASCADE"
    )

    class Meta:
        table_name = "compromiso_contacto"
        primary_key = CompositeKey("id_actividad", "id_contacto")


class Recordatorios(BaseModel):
    id_recordatorio = AutoField()
    id_actividad = ForeignKeyField(
        Actividades,
        column_name="id_actividad",
        backref="recordatorios",
        on_delete="CASCADE",
    )
    fecha_hora = DateTimeField()
    mensaje = CharField()
    enviado = BooleanField(default=False, null=True)

    class Meta:
        table_name = "recordatorios"


MODELS = [
    Usuarios,
    Agendas,
    Categorias,
    PatronesRecurrencia,
    Actividades,
    Tareas,
    Eventos,
    Compromisos,
    Contactos,
    CompromisoContacto,
    Recordatorios,
]
