from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

PASSWORD = "RitmoSeguro!9274Mundo"

class AutenticacionTests(TestCase):
    def datos(self, **cambios):
        datos = {"username": "estudiante", "password1": PASSWORD, "password2": PASSWORD}
        datos.update(cambios)
        return datos

    def test_registro_guarda_hash_y_no_da_permisos_administrativos(self):
        respuesta = self.client.post(reverse("registro"), self.datos())
        self.assertRedirects(respuesta, reverse("login"))
        usuario = get_user_model().objects.get(username="estudiante")
        self.assertTrue(usuario.check_password(PASSWORD))
        self.assertNotEqual(usuario.password, PASSWORD)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)

    def test_registro_rechaza_usuario_repetido(self):
        self.client.post(reverse("registro"), self.datos())
        respuesta = self.client.post(reverse("registro"), self.datos())
        self.assertTrue(respuesta.context["form"].errors.get("username"))
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_registro_rechaza_claves_distintas(self):
        respuesta = self.client.post(reverse("registro"), self.datos(password2="Otra!Clave9274"))
        self.assertTrue(respuesta.context["form"].errors.get("password2"))
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_registro_rechaza_clave_debil(self):
        respuesta = self.client.post(reverse("registro"), self.datos(password1="123", password2="123"))
        self.assertTrue(respuesta.context["form"].errors.get("password2"))
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_registro_campos_vacios(self):
        respuesta = self.client.post(reverse("registro"), {})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 0)

    def usuario(self):
        return get_user_model().objects.create_user(username="estudiante", password=PASSWORD)

    def test_login_valido_y_cuenta_protegida(self):
        self.usuario()
        respuesta = self.client.post(reverse("login"), {"username": "estudiante", "password": PASSWORD})
        self.assertRedirects(respuesta, reverse("cuenta"))
        self.assertIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(reverse("cuenta")), "Hola, estudiante")

    def test_login_invalido_no_crea_sesion(self):
        self.usuario()
        respuesta = self.client.post(reverse("login"), {"username": "estudiante", "password": "incorrecta"})
        self.assertTrue(respuesta.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_usuario_inactivo_no_accede(self):
        usuario = self.usuario()
        usuario.is_active = False
        usuario.save()
        respuesta = self.client.post(reverse("login"), {"username": "estudiante", "password": PASSWORD})
        self.assertTrue(respuesta.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_cuenta_sin_sesion_redirige(self):
        respuesta = self.client.get(reverse("cuenta"))
        self.assertRedirects(respuesta, reverse("login") + "?next=" + reverse("cuenta"))

    def test_login_no_redirige_a_sitio_externo(self):
        self.usuario()
        respuesta = self.client.post(reverse("login"), {"username": "estudiante", "password": PASSWORD, "next": "https://example.org"})
        self.assertRedirects(respuesta, reverse("cuenta"))

    def test_logout_post_invalida_sesion(self):
        self.client.force_login(self.usuario())
        respuesta = self.client.post(reverse("logout"))
        self.assertRedirects(respuesta, reverse("votaciones:inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(self.client.get(reverse("cuenta")).status_code, 302)

    def test_logout_get_no_cierra_sesion(self):
        self.client.force_login(self.usuario())
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_csrf_requerido_para_registro_login_y_logout(self):
        cliente = Client(enforce_csrf_checks=True)
        for nombre in ["registro", "login", "logout"]:
            with self.subTest(nombre=nombre):
                self.assertEqual(cliente.post(reverse(nombre), {}).status_code, 403)

    def test_votante_no_accede_al_panel_admin(self):
        self.client.force_login(self.usuario())
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)
        self.assertNotContains(self.client.get(reverse("cuenta")), "Administrar")

    def test_registrado_no_crea_cuenta_adicional(self):
        self.client.force_login(self.usuario())
        self.assertRedirects(self.client.get(reverse("registro")), reverse("cuenta"))
