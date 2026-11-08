import csv
import io
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from .models import Categoria, Edicion, Opcion, Votacion, Voto
from .services import registrar_voto


class GestionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(username='operador', is_staff=True, password='clave_demo_9182')
        cls.votante = User.objects.create_user(username='votante', password='clave_demo_9182')
        cls.edicion = Edicion.objects.create(nombre='Festival', anio=2027)
        cls.categoria = Categoria.objects.create(nombre='Acordeón', edicion=cls.edicion, habilitada=True)
        cls.subevento = Votacion.objects.create(titulo='Final', categoria=cls.categoria)
        cls.opcion = Opcion.objects.create(nombre='Participante A', votacion=cls.subevento)

    def setUp(self):
        self.client.force_login(self.staff)

    def test_gestion_acceso_restringido_y_metodos(self):
        rutas = [reverse('gestion:inicio'), reverse('gestion:votos'), reverse('gestion:informe'), reverse('gestion:informe_csv'), reverse('gestion:listado', args=['ediciones']), reverse('gestion:crear', args=['opciones']), reverse('gestion:archivar', args=['ediciones', self.edicion.pk])]
        for url in rutas:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get(reverse('gestion:listado', args=['arbitrario'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('gestion:restaurar', args=['ediciones', self.edicion.pk])).status_code, 405)
        self.client.force_login(self.votante)
        for url in rutas:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(reverse('gestion:archivar', args=['ediciones', self.edicion.pk])).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('gestion:inicio')).status_code, 302)

    def test_creacion_edicion_categoria_subevento_opcion(self):
        casos = [
            ('ediciones', {'nombre': 'Nueva edición', 'anio': 2028}, Edicion),
            ('categorias', {'nombre': 'Canción', 'edicion': self.edicion.pk, 'habilitada': 'on'}, Categoria),
            ('subeventos', {'titulo': 'Ronda inicial', 'categoria': self.categoria.pk, 'habilitada': 'on'}, Votacion),
            ('opciones', {'nombre': 'Participante B', 'votacion': self.subevento.pk}, Opcion),
        ]
        for tipo, datos, modelo in casos:
            with self.subTest(tipo=tipo):
                antes = modelo.objects.count()
                respuesta = self.client.post(reverse('gestion:crear', args=[tipo]), datos)
                self.assertEqual(respuesta.status_code, 302)
                self.assertEqual(modelo.objects.count(), antes + 1)
        self.assertTrue(Categoria.objects.get(nombre='Canción').habilitada)

    def test_formulario_valida_unicidad_y_rechaza_padre_inexistente(self):
        r = self.client.post(reverse('gestion:crear', args=['ediciones']), {'nombre': 'Otra', 'anio': 2027})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)
        r = self.client.post(reverse('gestion:crear', args=['categorias']), {'nombre': 'Acordeón', 'edicion': self.edicion.pk})
        self.assertTrue(r.context['form'].errors)
        r = self.client.post(reverse('gestion:crear', args=['opciones']), {'nombre': 'No válida', 'votacion': 99999})
        self.assertTrue(r.context['form'].errors)
        self.assertFalse(Opcion.objects.filter(nombre='No válida').exists())

    def test_edicion_de_datos_y_cierre_de_categoria(self):
        r = self.client.post(reverse('gestion:editar', args=['categorias', self.categoria.pk]), {'nombre': 'Acordeón actualizado', 'edicion': self.edicion.pk, 'descripcion': 'actualizado'})
        self.assertEqual(r.status_code, 302)
        self.categoria.refresh_from_db()
        self.assertFalse(self.categoria.habilitada)
        self.assertEqual(self.categoria.nombre, 'Acordeón actualizado')
        self.client.force_login(self.votante)
        self.assertEqual(self.client.get(reverse('votaciones:votar', args=[self.categoria.pk])).status_code, 403)

    def test_archivar_y_restaurar_cada_nivel_conserva_votos_y_oculta_publico(self):
        registrar_voto(usuario=self.votante, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)
        objetos = [('ediciones', self.edicion), ('categorias', self.categoria), ('subeventos', self.subevento), ('opciones', self.opcion)]
        for tipo, obj in objetos:
            with self.subTest(tipo=tipo):
                url = reverse('gestion:archivar', args=[tipo, obj.pk])
                self.assertContains(self.client.get(url), '¿Deseas archivar')
                obj.refresh_from_db()
                self.assertTrue(obj.activo)
                self.assertEqual(self.client.post(url).status_code, 302)
                obj.refresh_from_db()
                self.assertFalse(obj.activo)
                self.assertEqual(Voto.objects.count(), 1)
                data = self.client.get(reverse('api_categorias')).json()['categorias']
                if tipo in ('ediciones', 'categorias'):
                    self.assertEqual(data, [])
                else:
                    self.assertEqual(data[0]['opciones'], [])
                self.assertEqual(self.client.post(reverse('gestion:restaurar', args=[tipo, obj.pk])).status_code, 302)
                obj.refresh_from_db()
                self.assertTrue(obj.activo)
        self.assertEqual(Voto.objects.get().opcion_id, self.opcion.pk)

    def test_opcion_archivada_no_aparece_ni_acepta_voto(self):
        self.client.post(reverse('gestion:archivar', args=['opciones', self.opcion.pk]))
        self.client.force_login(self.votante)
        r = self.client.get(reverse('votaciones:detalle', args=[self.subevento.pk]))
        self.assertNotContains(r, self.opcion.nombre)
        r = self.client.post(reverse('votaciones:votar', args=[self.categoria.pk]), {'opcion': self.opcion.pk, 'confirmar': '1'})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Voto.objects.exists())

    def test_no_reasignar_relaciones_si_hay_votos(self):
        registrar_voto(usuario=self.votante, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)
        otro = Edicion.objects.create(nombre='Otro festival', anio=2028)
        respuesta = self.client.post(reverse('gestion:editar', args=['categorias', self.categoria.pk]), {'nombre': self.categoria.nombre, 'edicion': otro.pk, 'habilitada': 'on'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].errors)
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.edicion_id, self.edicion.pk)

    def test_informe_csv_agrupado_sin_duplicacion_y_sin_identidad(self):
        registrar_voto(usuario=self.votante, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)
        Opcion.objects.create(nombre='B', votacion=self.subevento)
        r = self.client.get(reverse('gestion:informe_csv'))
        filas = list(csv.reader(io.StringIO(r.content.decode('utf-8-sig'))))
        self.assertEqual(filas[1][-2:], ['2', '1'])
        self.assertNotIn('votante', r.content.decode('utf-8'))
        self.categoria.nombre = '=1+1'
        self.categoria.save()
        r = self.client.get(reverse('gestion:informe_csv'))
        self.assertIn("'=1+1", r.content.decode('utf-8'))

    def test_csrf_es_obligatorio_en_mutaciones(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.staff)
        for url in [reverse('gestion:crear', args=['ediciones']), reverse('gestion:archivar', args=['ediciones', self.edicion.pk]), reverse('gestion:restaurar', args=['ediciones', self.edicion.pk])]:
            self.assertEqual(cliente.post(url, {} ).status_code, 403)
        self.edicion.refresh_from_db()
        self.assertTrue(self.edicion.activo)

    def test_consulta_votos_lectura(self):
        registrar_voto(usuario=self.votante, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)
        r = self.client.get(reverse('gestion:votos'))
        for texto in ['votante', 'Acordeón', 'Participante A', '2027']:
            self.assertContains(r, texto)
        self.assertEqual(self.client.post(reverse('gestion:votos'), {}).status_code, 405)
