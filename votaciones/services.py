"""Único flujo de escritura de votos de la aplicación pública."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from .models import Categoria, Opcion, Voto


class VotoDuplicado(ValidationError):
    pass


def registrar_voto(*, usuario, categoria_id, opcion_id):
    if not usuario.is_authenticated or not usuario.is_active:
        raise PermissionDenied("Debes iniciar sesión para votar.")
    try:
        with transaction.atomic():
            # Un bloqueo por PK serializa las confirmaciones en esta categoría.
            # Se relee su estado en la transacción, sin confiar en la pantalla previa.
            categoria = Categoria.objects.select_for_update().get(pk=categoria_id)
            if not categoria.activo or not categoria.edicion.activo:
                raise ValidationError("Esta categoría o su edición ya no está disponible.")
            if not categoria.habilitada:
                raise ValidationError("Esta categoría está cerrada.")
            if Voto.objects.filter(usuario=usuario, categoria=categoria).exists():
                raise VotoDuplicado("Ya registraste un voto en esta categoría y edición.")
            try:
                opcion = (
                    Opcion.objects.select_for_update().select_related("votacion")
                    .get(pk=opcion_id, activo=True, votacion__activo=True, votacion__categoria_id=categoria.pk)
                )
            except Opcion.DoesNotExist:
                raise ValidationError("La opción no pertenece a esta categoría y edición.") from None
            if not opcion.votacion.habilitada:
                raise ValidationError("Este subevento está cerrado.")
            return Voto.objects.create(usuario=usuario, categoria=categoria, opcion=opcion)
    except IntegrityError:
        # Se consulta DESPUÉS de salir de atomic(), con la transacción recuperada.
        # La restricción UNIQUE es la protección final frente a otros escritores.
        if Voto.objects.filter(usuario=usuario, categoria_id=categoria_id).exists():
            raise VotoDuplicado("Ya registraste un voto en esta categoría y edición.") from None
        raise
