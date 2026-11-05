from django.core.management.base import BaseCommand
from django.db import transaction

from votaciones.models import Categoria, Edicion, Opcion, Votacion


class Command(BaseCommand):
    help = "Agrega catálogo ficticio del Eje 3 sin borrar datos, crear usuarios ni emitir votos."

    @transaction.atomic
    def handle(self, *args, **options):
        edicion, _ = Edicion.objects.get_or_create(
            anio=2027, defaults={"nombre": "Festival de la Leyenda Vallenata"},
        )
        escenarios = [
            ("Demo - Acordeón", True, [("Demo - Primera ronda", ["Demo - Participante A", "Demo - Participante B"]), ("Demo - Segunda ronda", ["Demo - Participante C"])]),
            ("Demo - Canción", True, [("Demo - Canciones", ["Demo - Canción A", "Demo - Canción B"])]),
            ("Demo - Cerrada", False, [("Demo - Subevento cerrado por categoría", ["Demo - Opción cerrada"])]),
        ]
        for nombre, habilitada, subeventos in escenarios:
            categoria, _ = Categoria.objects.get_or_create(
                edicion=edicion, nombre=nombre,
                defaults={"descripcion": "Datos ficticios para comprobar el Eje 3.", "habilitada": habilitada},
            )
            for titulo, opciones in subeventos:
                votacion, _ = Votacion.objects.get_or_create(categoria=categoria, titulo=titulo)
                for opcion in opciones:
                    Opcion.objects.get_or_create(votacion=votacion, nombre=opcion)
        self.stdout.write(self.style.SUCCESS("Catálogo de demostración preparado. No se modificaron votos ni usuarios."))
        self.stdout.write("Las categorías existentes conservan su estado. Revisar Habilitada en Admin si ya se habían cerrado.")
