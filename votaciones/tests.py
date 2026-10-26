from django.test import TestCase
from django.urls import reverse
from .models import Edicion, Categoria, Votacion, Opcion

class CatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.edicion = Edicion.objects.create(nombre="Festival local", anio=2027)
        cls.categoria = Categoria.objects.create(edicion=cls.edicion, nombre="Categoria uno")
        cls.votacion = Votacion.objects.create(categoria=cls.categoria, titulo="Votacion uno")
        cls.opcion = Opcion.objects.create(votacion=cls.votacion, nombre="Opcion uno")
        otra = Edicion.objects.create(nombre="Otra edicion", anio=2028)
        otra_cat = Categoria.objects.create(edicion=otra, nombre="Categoria ajena")
        otra_vot = Votacion.objects.create(categoria=otra_cat, titulo="Votacion ajena")
        Opcion.objects.create(votacion=otra_vot, nombre="Opcion ajena")

    def test_inicio_y_ediciones_publicos(self):
        for nombre in ["inicio", "ediciones"]:
            respuesta = self.client.get(reverse("votaciones:" + nombre))
            self.assertContains(respuesta, "Festival local")
            self.assertContains(respuesta, "Otra edicion")

    def test_categorias_filtradas_por_edicion(self):
        respuesta = self.client.get(reverse("votaciones:categorias", args=[self.edicion.pk]))
        self.assertContains(respuesta, "Categoria uno")
        self.assertNotContains(respuesta, "Categoria ajena")

    def test_votaciones_filtradas_por_categoria(self):
        respuesta = self.client.get(reverse("votaciones:votaciones", args=[self.categoria.pk]))
        self.assertContains(respuesta, "Votacion uno")
        self.assertNotContains(respuesta, "Votacion ajena")

    def test_opciones_filtradas_por_votacion(self):
        respuesta = self.client.get(reverse("votaciones:detalle", args=[self.votacion.pk]))
        self.assertContains(respuesta, "Opcion uno")
        self.assertNotContains(respuesta, "Opcion ajena")

    def test_nuevos_registros_y_ediciones_se_reflejan(self):
        self.opcion.nombre = "Nombre actualizado"
        self.opcion.save()
        Opcion.objects.create(votacion=self.votacion, nombre="Opcion nueva")
        respuesta = self.client.get(reverse("votaciones:detalle", args=[self.votacion.pk]))
        self.assertContains(respuesta, "Nombre actualizado")
        self.assertContains(respuesta, "Opcion nueva")
        self.assertNotContains(respuesta, "Opcion uno")

    def test_identificadores_inexistentes_404(self):
        for nombre in ["categorias", "votaciones", "detalle"]:
            with self.subTest(nombre=nombre):
                self.assertEqual(self.client.get(reverse("votaciones:" + nombre, args=[99999])).status_code, 404)

    def test_mensajes_catalogo_vacio(self):
        Opcion.objects.all().delete()
        self.assertContains(self.client.get(reverse("votaciones:detalle", args=[self.votacion.pk])), "Aún no hay opciones")
        Votacion.objects.all().delete()
        self.assertContains(self.client.get(reverse("votaciones:votaciones", args=[self.categoria.pk])), "Aún no hay votaciones")
        Categoria.objects.all().delete()
        self.assertContains(self.client.get(reverse("votaciones:categorias", args=[self.edicion.pk])), "Aún no hay categorías")
        Edicion.objects.all().delete()
        self.assertContains(self.client.get(reverse("votaciones:ediciones")), "No hay ediciones")
        self.assertContains(self.client.get(reverse("votaciones:inicio")), "El catálogo se está preparando")

    def test_contenido_escapado(self):
        self.opcion.nombre = '<script>alert("x")</script>'
        self.opcion.save()
        respuesta = self.client.get(reverse("votaciones:detalle", args=[self.votacion.pk]))
        self.assertContains(respuesta, "&lt;script&gt;")
        self.assertNotContains(respuesta, '<script>alert("x")</script>')

    def test_consultas_detalle_sin_n_mas_uno(self):
        # Una consulta para la votacion y sus padres; otra para todas sus opciones.
        with self.assertNumQueries(2):
            self.client.get(reverse("votaciones:detalle", args=[self.votacion.pk]))
