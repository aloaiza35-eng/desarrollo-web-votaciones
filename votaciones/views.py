from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from .models import Categoria, Edicion, Opcion, Votacion


def inicio(request):
    ediciones = Edicion.objects.annotate(total_categorias=Count("categorias")).order_by("-anio")
    return render(request, "votaciones/inicio.html", {
        "ediciones": ediciones[:3],
        "total_ediciones": Edicion.objects.count(),
        "total_categorias": Categoria.objects.count(),
        "total_votaciones": Votacion.objects.count(),
        "total_opciones": Opcion.objects.count(),
    })


def ediciones(request):
    return render(request, "votaciones/ediciones.html", {
        "ediciones": Edicion.objects.annotate(total_categorias=Count("categorias")).order_by("-anio"),
    })


def categorias(request, edicion_id):
    edicion = get_object_or_404(Edicion, pk=edicion_id)
    categorias = edicion.categorias.annotate(total_votaciones=Count("votaciones"))
    return render(request, "votaciones/categorias.html", {"edicion": edicion, "categorias": categorias})


def votaciones(request, categoria_id):
    categoria = get_object_or_404(Categoria.objects.select_related("edicion"), pk=categoria_id)
    votaciones = categoria.votaciones.annotate(total_opciones=Count("opciones"))
    return render(request, "votaciones/votaciones.html", {"categoria": categoria, "votaciones": votaciones})


def detalle(request, votacion_id):
    votacion = get_object_or_404(
        Votacion.objects.select_related("categoria__edicion").prefetch_related("opciones"),
        pk=votacion_id,
    )
    return render(request, "votaciones/detalle.html", {"votacion": votacion})
