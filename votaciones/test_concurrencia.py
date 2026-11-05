"""CP-09 real: dos POST concurrentes con conexiones MySQL independientes."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.test import Client, TransactionTestCase
from django.urls import reverse

from .models import Categoria, Edicion, Opcion, Votacion, Voto


@skipUnless(connection.vendor == "mysql", "CP-09 requiere MySQL; SQLite no valida el bloqueo de filas.")
class ConcurrenciaMySQLTests(TransactionTestCase):
    def test_bd_rechaza_inserciones_simultaneas_sin_el_servicio(self):
        usuario = get_user_model().objects.create_user(username="insercion_directa")
        edicion = Edicion.objects.create(nombre="Integridad concurrente", anio=2027)
        categoria = Categoria.objects.create(edicion=edicion, nombre="Categoría", habilitada=True)
        subevento = Votacion.objects.create(categoria=categoria, titulo="Ronda")
        opcion = Opcion.objects.create(votacion=subevento, nombre="Opción")
        barrera = Barrier(2, timeout=15)

        def insertar(_):
            close_old_connections()
            try:
                barrera.wait()
                with transaction.atomic():
                    # Omite incluso save()/full_clean(): comprueba el índice MySQL.
                    Voto.objects.bulk_create([Voto(usuario_id=usuario.pk, categoria_id=categoria.pk, opcion_id=opcion.pk)])
                return "registrado"
            except IntegrityError:
                return "duplicado"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as ejecutor:
            resultados = list(ejecutor.map(insertar, [1, 2]))
        self.assertEqual(sorted(resultados), ["duplicado", "registrado"])
        self.assertEqual(Voto.objects.count(), 1)

    def test_cp09_dos_post_mismo_usuario_diferentes_subeventos(self):
        usuario = get_user_model().objects.create_user(username="concurrente")
        edicion = Edicion.objects.create(nombre="Prueba concurrente", anio=2027)
        categoria = Categoria.objects.create(edicion=edicion, nombre="Categoría concurrente", habilitada=True)
        opciones = []
        for numero in [1, 2]:
            subevento = Votacion.objects.create(categoria=categoria, titulo=f"Subevento {numero}")
            opciones.append(Opcion.objects.create(votacion=subevento, nombre=f"Opción {numero}"))
        url = reverse("votaciones:votar", args=[categoria.pk])
        barrera = Barrier(2, timeout=15)

        def enviar(opcion_id):
            close_old_connections()
            try:
                cliente = Client()
                cliente.force_login(get_user_model().objects.get(pk=usuario.pk))
                barrera.wait()
                respuesta = cliente.post(url, {"opcion": opcion_id, "confirmar": "1"})
                return respuesta.status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as ejecutor:
            resultados = list(ejecutor.map(enviar, [o.pk for o in opciones]))
        self.assertEqual(sorted(resultados), [302, 409])
        self.assertEqual(Voto.objects.filter(usuario=usuario, categoria=categoria).count(), 1)
