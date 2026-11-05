from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Categoria, Edicion, Opcion, Votacion, Voto
from .services import VotoDuplicado, registrar_voto


class EscenarioVotos(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username="votante")
        cls.otro = get_user_model().objects.create_user(username="otro")
        cls.edicion = Edicion.objects.create(nombre="Festival de prueba", anio=2027)
        cls.categoria = Categoria.objects.create(edicion=cls.edicion, nombre="Acordeón", habilitada=True)
        cls.subevento = Votacion.objects.create(categoria=cls.categoria, titulo="Primera ronda")
        cls.opcion = Opcion.objects.create(votacion=cls.subevento, nombre="Opción A")
        cls.opcion_b = Opcion.objects.create(votacion=cls.subevento, nombre="Opción B")
        segundo = Votacion.objects.create(categoria=cls.categoria, titulo="Segunda ronda")
        cls.opcion_otro_subevento = Opcion.objects.create(votacion=segundo, nombre="Opción C")
        cls.otra_categoria = Categoria.objects.create(edicion=cls.edicion, nombre="Canción", habilitada=True)
        otra_votacion = Votacion.objects.create(categoria=cls.otra_categoria, titulo="Canciones")
        cls.opcion_otra_categoria = Opcion.objects.create(votacion=otra_votacion, nombre="Canción A")
        otra_edicion = Edicion.objects.create(nombre="Festival siguiente", anio=2028)
        cls.categoria_otra_edicion = Categoria.objects.create(edicion=otra_edicion, nombre="Acordeón", habilitada=True)
        otro_evento = Votacion.objects.create(categoria=cls.categoria_otra_edicion, titulo="Ronda 2028")
        cls.opcion_otra_edicion = Opcion.objects.create(votacion=otro_evento, nombre="Opción 2028")

    def setUp(self):
        self.client.force_login(self.usuario)
        self.url = reverse("votaciones:votar", args=[self.categoria.pk])

    def votar(self, opcion=None, categoria=None, **extra):
        datos = {"opcion": (opcion or self.opcion).pk, "confirmar": "1", **extra}
        url = reverse("votaciones:votar", args=[(categoria or self.categoria).pk])
        return self.client.post(url, datos)

    def guardar(self):
        return registrar_voto(usuario=self.usuario, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)


class FlujoVotosTests(EscenarioVotos):
    def test_cp01_seleccionar_confirmar_y_guardar(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)
        respuesta = self.client.post(self.url, {"opcion": self.opcion.pk})
        self.assertContains(respuesta, "Revisa tu elección")
        self.assertEqual(Voto.objects.count(), 0)
        self.assertRedirects(self.votar(), reverse("votaciones:participacion"))
        voto = Voto.objects.get()
        self.assertEqual((voto.usuario, voto.categoria, voto.opcion), (self.usuario, self.categoria, self.opcion))
        self.assertEqual(voto.edicion, self.edicion)
        self.assertIsNotNone(voto.fecha)

    def test_cp02_bloquea_misma_opcion_otra_opcion_y_otro_subevento(self):
        self.votar()
        for opcion in [self.opcion, self.opcion_b, self.opcion_otro_subevento]:
            with self.subTest(opcion=opcion.nombre):
                self.assertContains(self.votar(opcion), "Ya registraste un voto", status_code=409)
        self.assertEqual(Voto.objects.count(), 1)

    def test_cp03_permite_otra_categoria_y_otra_edicion(self):
        self.votar()
        self.assertEqual(self.votar(self.opcion_otra_categoria, self.otra_categoria).status_code, 302)
        self.assertEqual(self.votar(self.opcion_otra_edicion, self.categoria_otra_edicion).status_code, 302)
        self.assertEqual(Voto.objects.filter(usuario=self.usuario).count(), 3)

    def test_cp04_sin_sesion_no_guarda_get_ni_post(self):
        self.client.logout()
        self.assertRedirects(self.client.get(self.url), reverse("login") + "?next=" + self.url)
        respuesta = self.client.post(self.url, {"opcion": self.opcion.pk, "confirmar": "1"})
        self.assertRedirects(respuesta, reverse("login") + "?next=" + self.url)
        self.assertFalse(Voto.objects.exists())

    def test_cp05_categoria_cerrada(self):
        self.categoria.habilitada = False
        self.categoria.save()
        self.assertContains(self.votar(), "categoría está cerrada", status_code=403)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertFalse(Voto.objects.exists())

    def test_cp05_categoria_cierra_entre_seleccion_y_confirmacion(self):
        self.client.post(self.url, {"opcion": self.opcion.pk})
        Categoria.objects.filter(pk=self.categoria.pk).update(habilitada=False)
        self.assertEqual(self.votar().status_code, 403)
        self.assertFalse(Voto.objects.exists())

    def test_cp06_rechaza_opcion_otra_categoria_y_edicion(self):
        for opcion in [self.opcion_otra_categoria, self.opcion_otra_edicion]:
            self.assertEqual(self.votar(opcion).status_code, 400)
        self.assertFalse(Voto.objects.exists())

    def test_cp07_historial_solo_del_usuario(self):
        self.guardar()
        registrar_voto(usuario=self.otro, categoria_id=self.otra_categoria.pk, opcion_id=self.opcion_otra_categoria.pk)
        respuesta = self.client.get(reverse("votaciones:participacion"))
        self.assertContains(respuesta, "Opción A")
        self.assertContains(respuesta, "2027")
        self.assertNotContains(respuesta, "Canción A")
        self.assertEqual(list(respuesta.context["votos"].values_list("usuario_id", flat=True)), [self.usuario.pk])

    def test_historial_vacio_y_sin_sesion(self):
        self.assertContains(self.client.get(reverse("votaciones:participacion")), "Aún no has registrado votos")
        self.client.logout()
        self.assertEqual(self.client.get(reverse("votaciones:participacion")).status_code, 302)

    def test_subevento_cerrado_rechaza_post_y_no_se_ofrece(self):
        self.subevento.habilitada = False
        self.subevento.save()
        self.assertEqual(self.votar().status_code, 400)
        self.assertNotContains(self.client.get(self.url), "Opción A")
        self.assertContains(self.client.get(reverse("votaciones:detalle", args=[self.subevento.pk])), "Votación cerrada")
        self.assertFalse(Voto.objects.exists())

    def test_csrf_ausente_rechazado_y_token_valido_aceptado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        self.assertEqual(cliente.post(self.url, {"opcion": self.opcion.pk, "confirmar": "1"}).status_code, 403)
        cliente.get(self.url)
        token = cliente.cookies["csrftoken"].value
        respuesta = cliente.post(self.url, {"opcion": self.opcion.pk, "confirmar": "1", "csrfmiddlewaretoken": token})
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Voto.objects.count(), 1)

    def test_get_nunca_registra_voto_y_muestra_confirmacion_solo_por_post(self):
        self.assertEqual(self.client.get(self.url, {"opcion": self.opcion.pk, "confirmar": "1"}).status_code, 200)
        self.assertFalse(Voto.objects.exists())
        self.assertEqual(self.client.put(self.url).status_code, 405)

    def test_identificadores_invalidos_y_categoria_inexistente(self):
        for identificador in ["", "abc", "-1", "99999999999999999999999999999"]:
            self.assertEqual(self.client.post(self.url, {"opcion": identificador, "confirmar": "1"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("votaciones:votar", args=[99999])).status_code, 404)
        self.assertFalse(Voto.objects.exists())

    def test_usuario_enviado_por_cliente_no_suplanta_sesion(self):
        self.votar(usuario=self.otro.pk)
        self.assertEqual(Voto.objects.get().usuario, self.usuario)

    def test_categoria_sin_opciones_habilitadas(self):
        Votacion.objects.filter(categoria=self.categoria).update(habilitada=False)
        self.assertContains(self.client.get(self.url), "No hay opciones habilitadas")
        self.assertEqual(self.votar().status_code, 400)

    def test_detalle_bloquea_otro_subevento_despues_de_votar(self):
        self.guardar()
        respuesta = self.client.get(reverse("votaciones:detalle", args=[self.opcion_otro_subevento.votacion_id]))
        self.assertContains(respuesta, "Ya participaste en esta categoría")
        self.assertNotContains(respuesta, "Elegir esta opción")

    def test_confirmacion_escapa_html_en_opcion(self):
        self.opcion.nombre = '<script>alert("x")</script>'
        self.opcion.save()
        respuesta = self.client.post(self.url, {"opcion": self.opcion.pk})
        self.assertContains(respuesta, "&lt;script&gt;")
        self.assertNotContains(respuesta, self.opcion.nombre)


class IntegridadVotosTests(EscenarioVotos):
    def test_unicidad_en_bd_incluso_sin_validacion_de_formulario(self):
        self.guardar()
        # bulk_create omite save()/full_clean(): se exige que lo rechace MySQL/SQLite.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Voto.objects.bulk_create([Voto(usuario=self.usuario, categoria=self.categoria, opcion=self.opcion_otro_subevento)])
        self.assertEqual(Voto.objects.count(), 1)

    def test_servicio_no_autorizado_o_inactivo(self):
        for usuario in [AnonymousUser(), self.usuario]:
            if usuario == self.usuario:
                usuario.is_active = False
            with self.assertRaises(PermissionDenied):
                registrar_voto(usuario=usuario, categoria_id=self.categoria.pk, opcion_id=self.opcion.pk)
        self.assertFalse(Voto.objects.exists())

    def test_servicio_revalida_pertenencia_y_estado(self):
        with self.assertRaises(ValidationError):
            registrar_voto(usuario=self.usuario, categoria_id=self.categoria.pk, opcion_id=self.opcion_otra_edicion.pk)
        Votacion.objects.filter(pk=self.subevento.pk).update(habilitada=False)
        with self.assertRaises(ValidationError):
            self.guardar()
        Categoria.objects.filter(pk=self.categoria.pk).update(habilitada=False)
        with self.assertRaises(ValidationError):
            self.guardar()
        self.assertFalse(Voto.objects.exists())

    def test_servicio_detecta_duplicado(self):
        self.guardar()
        with self.assertRaises(VotoDuplicado):
            registrar_voto(usuario=self.usuario, categoria_id=self.categoria.pk, opcion_id=self.opcion_otro_subevento.pk)

    def test_modelo_rechaza_relaciones_incompatibles(self):
        with self.assertRaises(ValidationError):
            Voto.objects.create(usuario=self.usuario, categoria=self.categoria, opcion=self.opcion_otra_categoria)

    def test_voto_guardado_no_se_puede_editar(self):
        voto = self.guardar()
        voto.opcion = self.opcion_b
        with self.assertRaises(ValidationError):
            voto.save()
        voto.refresh_from_db()
        self.assertEqual(voto.opcion, self.opcion)

    def test_no_reasignar_catalogo_con_votos(self):
        self.guardar()
        self.categoria.edicion = self.categoria_otra_edicion.edicion
        with self.assertRaises(ValidationError):
            self.categoria.full_clean()
        self.subevento.categoria = self.otra_categoria
        with self.assertRaises(ValidationError):
            self.subevento.full_clean()
        self.opcion.votacion = self.opcion_otro_subevento.votacion
        with self.assertRaises(ValidationError):
            self.opcion.full_clean()

    def test_borrado_protegido_de_datos_referenciados(self):
        self.guardar()
        for objeto in [self.usuario, self.categoria, self.opcion, self.subevento, self.edicion]:
            with self.assertRaises(ProtectedError):
                objeto.delete()

    def test_integrityerror_no_relacionado_no_se_disfraza_como_duplicado(self):
        with patch("votaciones.services.Voto.objects.create", side_effect=IntegrityError("otra restricción")):
            with self.assertRaises(IntegrityError):
                self.guardar()

    def test_estado_releido_tras_validar_formulario(self):
        from .services import registrar_voto as real

        def cerrar_antes_de_guardar(**kwargs):
            Categoria.objects.filter(pk=self.categoria.pk).update(habilitada=False)
            return real(**kwargs)

        with patch("votaciones.views.registrar_voto", side_effect=cerrar_antes_de_guardar):
            self.assertContains(self.votar(), "categoría está cerrada", status_code=400)
        self.assertFalse(Voto.objects.exists())


class ApiYAdminTests(EscenarioVotos):
    def test_cp10_json_publico_con_datos_reales_y_sin_usuarios(self):
        self.client.logout()
        respuesta = self.client.get(reverse("api_categorias"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.headers["Content-Type"], "application/json")
        categoria = next(c for c in respuesta.json()["categorias"] if c["id"] == self.categoria.pk)
        self.assertEqual(categoria["edicion"]["anio"], 2027)
        self.assertTrue(categoria["habilitada"])
        self.assertEqual({o["id"] for o in categoria["opciones"]}, {self.opcion.pk, self.opcion_b.pk, self.opcion_otro_subevento.pk})
        self.assertNotIn("usuario", respuesta.content.decode())
        self.opcion.nombre = "Nombre actualizado desde la BD"
        self.opcion.save()
        self.assertContains(self.client.get(reverse("api_categorias")), self.opcion.nombre)

    def test_api_filtro_edicion_y_parametro_invalido(self):
        respuesta = self.client.get(reverse("api_categorias"), {"edicion": self.edicion.pk})
        self.assertEqual(len(respuesta.json()["categorias"]), 2)
        for dato in respuesta.json()["categorias"]:
            self.assertEqual(dato["edicion"]["id"], self.edicion.pk)
        for dato in ["abc", "0", "-1", "", "9" * 30]:
            self.assertEqual(self.client.get(reverse("api_categorias"), {"edicion": dato}).status_code, 400)

    def test_api_no_acepta_escrituras(self):
        self.assertEqual(self.client.post(reverse("api_categorias"), {}).status_code, 405)
        self.assertFalse(Voto.objects.exists())

    def test_api_cerradas_y_sin_opciones(self):
        categoria = Categoria.objects.create(edicion=self.edicion, nombre="Cerrada")
        respuesta = self.client.get(reverse("api_categorias"))
        dato = next(c for c in respuesta.json()["categorias"] if c["id"] == categoria.pk)
        self.assertFalse(dato["habilitada"])
        self.assertEqual(dato["opciones"], [])
        self.assertEqual(self.client.get(reverse("api_categorias"), {"edicion": 99999}).json(), {"categorias": []})

    def test_api_consultas_no_crecen_por_cada_categoria(self):
        with self.assertNumQueries(3):
            self.client.get(reverse("api_categorias"))

    def test_cp08_admin_consulta_registro_solo_lectura(self):
        voto = self.guardar()
        admin = get_user_model().objects.create_superuser(username="admin_prueba", password="SoloPruebas!123")
        self.client.force_login(admin)
        listado = reverse("admin:votaciones_voto_changelist")
        respuesta = self.client.get(listado)
        self.assertContains(respuesta, "votante")
        self.assertContains(respuesta, "Opción A")
        self.assertContains(respuesta, "2027")
        self.assertEqual(self.client.post(reverse("admin:votaciones_voto_change", args=[voto.pk]), {}).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:votaciones_voto_add")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:votaciones_voto_delete", args=[voto.pk])).status_code, 403)

    def test_votante_sin_acceso_admin(self):
        self.assertEqual(self.client.get(reverse("admin:votaciones_voto_changelist")).status_code, 302)

    def test_preparacion_demo_idempotente_y_sin_votos_ni_usuarios(self):
        antes = get_user_model().objects.count()
        call_command("preparar_demo_eje3", stdout=StringIO())
        cantidades = (Categoria.objects.count(), Votacion.objects.count(), Opcion.objects.count())
        call_command("preparar_demo_eje3", stdout=StringIO())
        self.assertEqual(cantidades, (Categoria.objects.count(), Votacion.objects.count(), Opcion.objects.count()))
        self.assertEqual(get_user_model().objects.count(), antes)
        self.assertFalse(Voto.objects.exists())
