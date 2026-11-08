from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Categoria, Votacion, Opcion


@require_GET
def categorias(request):
    consulta = Categoria.objects.filter(activo=True, edicion__activo=True).select_related("edicion").prefetch_related(
        Prefetch("votaciones", queryset=Votacion.objects.filter(activo=True).prefetch_related(
            Prefetch("opciones", queryset=Opcion.objects.filter(activo=True)))),
    ).order_by("-edicion__anio", "nombre", "pk")
    edicion = request.GET.get("edicion")
    if edicion is not None:
        try:
            edicion_id = int(edicion)
            if edicion_id <= 0 or edicion_id > 9223372036854775807:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({"error": "edicion debe ser un identificador entero positivo."}, status=400)
        consulta = consulta.filter(edicion_id=edicion_id)
    datos = []
    for categoria in consulta:
        datos.append({
            "id": categoria.pk,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "habilitada": categoria.habilitada,
            "edicion": {
                "id": categoria.edicion_id,
                "nombre": categoria.edicion.nombre,
                "anio": categoria.edicion.anio,
            },
            "opciones": [
                {
                    "id": opcion.pk,
                    "nombre": opcion.nombre,
                    "descripcion": opcion.descripcion,
                    "votacion": {
                        "id": votacion.pk, "titulo": votacion.titulo,
                        "habilitada": votacion.habilitada,
                    },
                }
                for votacion in categoria.votaciones.all()
                for opcion in votacion.opciones.all()
            ],
        })
    return JsonResponse({"categorias": datos}, json_dumps_params={"ensure_ascii": False, "indent": 2})
