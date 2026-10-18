from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tarea


class TareasTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.usuario = user_model.objects.create_user(
            username='ana',
            password='UnaClaveSegura-123!',
        )
        self.otro_usuario = user_model.objects.create_user(
            username='luis',
            password='OtraClaveSegura-456!',
        )
        self.tarea = Tarea.objects.create(
            usuario=self.usuario,
            nombre='Estudiar',
            descripcion='Repasar Django',
            fecha_vencimiento=date(2026, 10, 20),
        )

    def test_inicio_requiere_autenticacion(self):
        response = self.client.get(reverse('mis_tareas'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('mis_tareas')}",
        )

    def test_login_correcto_lleva_a_la_lista(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'ana', 'password': 'UnaClaveSegura-123!'},
        )

        self.assertRedirects(response, reverse('mis_tareas'))

    def test_solo_muestra_tareas_del_usuario_conectado(self):
        Tarea.objects.create(
            usuario=self.otro_usuario,
            nombre='Tarea privada',
            descripcion='No debe verse',
            fecha_vencimiento=date(2026, 10, 21),
        )
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('mis_tareas'))

        self.assertContains(response, 'Estudiar')
        self.assertNotContains(response, 'Tarea privada')

    def test_crea_tarea_asociada_al_usuario_conectado(self):
        self.client.force_login(self.usuario)

        response = self.client.post(
            reverse('crear_tarea'),
            {
                'nombre': 'Comprar leche',
                'descripcion': 'Al volver a casa',
                'fecha_vencimiento': '2026-10-22',
                'completada': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        tarea = Tarea.objects.get(nombre='Comprar leche')
        self.assertEqual(tarea.usuario, self.usuario)
        self.assertEqual(tarea.fecha_vencimiento, date(2026, 10, 22))

    def test_formulario_nuevo_precarga_fecha_del_calendario(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse('crear_tarea'),
            {'fecha': '2026-10-25'},
        )

        self.assertContains(
            response,
            '<input type="date" name="fecha_vencimiento" value="2026-10-25"',
            html=False,
        )

    def test_inicio_muestra_solo_pendientes_y_no_contiene_formulario(self):
        Tarea.objects.create(
            usuario=self.usuario,
            nombre='Ya terminada',
            descripcion='',
            fecha_vencimiento=date(2026, 10, 21),
            completada=True,
        )
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('mis_tareas'))

        self.assertContains(response, 'Estudiar')
        self.assertEqual(
            [tarea.nombre for tarea in response.context['tareas_pendientes']],
            ['Estudiar'],
        )
        self.assertContains(response, reverse('crear_tarea'))
        self.assertNotContains(response, 'id_fecha_vencimiento')

    def test_edita_tarea_propia_y_no_permite_editar_tarea_ajena(self):
        self.client.force_login(self.usuario)
        response = self.client.post(
            reverse('editar_tarea', args=[self.tarea.id]),
            {
                'nombre': 'Estudiar matemáticas',
                'descripcion': 'Repasar álgebra',
                'fecha_vencimiento': '2026-10-23',
                'completada': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.nombre, 'Estudiar matemáticas')
        self.assertTrue(self.tarea.completada)

        tarea_ajena = Tarea.objects.create(
            usuario=self.otro_usuario,
            nombre='Privada',
            descripcion='',
            fecha_vencimiento=date(2026, 10, 24),
        )
        response = self.client.get(
            reverse('editar_tarea', args=[tarea_ajena.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_elimina_solo_despues_de_confirmar(self):
        self.client.force_login(self.usuario)
        url = reverse('eliminar_tarea', args=[self.tarea.id])

        response = self.client.get(url)
        self.assertContains(response, '¿Seguro que quieres eliminar')
        self.assertTrue(Tarea.objects.filter(pk=self.tarea.id).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tarea.objects.filter(pk=self.tarea.id).exists())

    def test_registro_guarda_la_contrasena_con_hash(self):
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'maria',
                'password1': 'MiClaveNueva-908!',
                'password2': 'MiClaveNueva-908!',
            },
        )

        self.assertRedirects(response, reverse('login'))
        usuario = get_user_model().objects.get(username='maria')
        self.assertTrue(usuario.check_password('MiClaveNueva-908!'))
        self.assertNotEqual(usuario.password, 'MiClaveNueva-908!')
