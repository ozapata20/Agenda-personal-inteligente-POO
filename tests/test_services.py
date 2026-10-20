import unittest

from peewee import SqliteDatabase

from models import MODELS
from services.activities import ActividadService
from services.catalog import CategoriaService, ContactoService, RecurrenciaService
from services.reminders import RecordatorioService
from services.users import UsuarioService


class AgendaServicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_database = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
        cls.test_database.bind(MODELS)
        cls.test_database.connect()
        cls.test_database.create_tables(MODELS)

    @classmethod
    def tearDownClass(cls):
        cls.test_database.drop_tables(MODELS)
        cls.test_database.close()

    def setUp(self):
        self.user, self.agenda = UsuarioService.crear(
            "Ana", f"ana{self.id()}@example.cl", "clave-larga-123"
        )

    def tearDown(self):
        UsuarioService.eliminar(self.user.id_usuario)

    def test_user_activity_and_task_crud(self):
        category = CategoriaService.crear("Estudio", "#123ABC")
        activity = ActividadService.crear(
            agenda_id=self.agenda.id_agenda,
            titulo="Informe",
            tipo_actividad="Tarea",
            fecha="2026-10-25",
            prioridad="Alta",
            categoria_id=category.id_categoria,
            fecha_vencimiento="2026-10-28",
        )
        self.assertEqual(len(ActividadService.listar(self.agenda.id_agenda)), 1)
        task = ActividadService.actualizar_avance_tarea(activity.id_actividad, 50)
        self.assertEqual(task.porcentaje_avance, 50)
        self.assertEqual(
            ActividadService.obtener_detalle(activity.id_actividad)["actividad"].estado,
            "En Proceso",
        )
        ActividadService.eliminar(activity.id_actividad)
        self.assertEqual(ActividadService.listar(self.agenda.id_agenda), [])
        CategoriaService.eliminar(category.id_categoria)

    def test_event_contact_commitment_and_reminder_crud(self):
        event = ActividadService.crear(
            agenda_id=self.agenda.id_agenda,
            titulo="Reunión",
            tipo_actividad="Evento",
            fecha="2026-10-25",
            hora_inicio="09:00",
            hora_fin="10:00",
        )
        self.assertEqual(
            ActividadService.obtener_detalle(event.id_actividad)["subtipo"].hora_inicio.hour,
            9,
        )
        commitment = ActividadService.crear(
            agenda_id=self.agenda.id_agenda,
            titulo="Llamar al equipo",
            tipo_actividad="Compromiso",
            fecha="2026-10-26",
        )
        contact = ContactoService.crear(self.user.id_usuario, "Luis")
        ActividadService.vincular_contacto(commitment.id_actividad, contact.id_contacto)
        self.assertEqual(
            len(ActividadService.listar_contactos(commitment.id_actividad)), 1
        )
        ActividadService.desvincular_contacto(
            commitment.id_actividad, contact.id_contacto
        )
        self.assertEqual(
            ActividadService.listar_contactos(commitment.id_actividad), []
        )
        reminder = RecordatorioService.crear(
            event.id_actividad, "2026-10-24 08:00", "Preparar reunión"
        )
        RecordatorioService.actualizar(
            reminder.id_recordatorio,
            "2026-10-24 08:30",
            "Revisar agenda",
            True,
        )
        self.assertTrue(RecordatorioService.listar(event.id_actividad)[0].enviado)
        RecordatorioService.eliminar(reminder.id_recordatorio)
        ContactoService.eliminar(contact.id_contacto)

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            ActividadService.crear(
                agenda_id=self.agenda.id_agenda,
                titulo="Tarea inválida",
                tipo_actividad="Tarea",
                fecha="25-10-2026",
            )
        with self.assertRaises(ValueError):
            ActividadService.actualizar_avance_tarea(1, 150)
        with self.assertRaises(ValueError):
            UsuarioService.crear("Duplicado", self.user.email, "clave-larga-123")

    def test_catalog_and_user_updates(self):
        updated_user = UsuarioService.actualizar(
            self.user.id_usuario, "Ana Actualizada", self.user.email
        )
        self.assertEqual(updated_user.nombre, "Ana Actualizada")

        category = CategoriaService.crear("Personal", "#AA00CC")
        category = CategoriaService.actualizar(
            category.id_categoria, "Trabajo", "#00AABB"
        )
        self.assertEqual(category.nombre, "Trabajo")
        self.assertEqual(category.color_hex, "#00AABB")
        CategoriaService.eliminar(category.id_categoria)

        contact = ContactoService.crear(self.user.id_usuario, "Luis")
        contact = ContactoService.actualizar(
            contact.id_contacto, "Luis Actualizado", "luis@example.cl", "5551234"
        )
        self.assertEqual(contact.nombre, "Luis Actualizado")
        ContactoService.eliminar(contact.id_contacto)

        pattern = RecurrenciaService.crear("Semanal", 1, "lunes")
        pattern = RecurrenciaService.actualizar(
            pattern.id_recurrencia, "Semanal", 2, "lunes,miércoles", "2026-12-31"
        )
        self.assertEqual(pattern.intervalo, 2)
        RecurrenciaService.eliminar(pattern.id_recurrencia)


if __name__ == "__main__":
    unittest.main()
