from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import SeleccionVotoForm
from .models import Categoria, Edicion, Opcion, Votacion, Voto
from .services import VotoDuplicado, registrar_voto


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
    voto = None
    if request.user.is_authenticated:
        voto = Voto.objects.filter(
            usuario=request.user, categoria_id=votacion.categoria_id,
        ).select_related("opcion").first()
    return render(request, "votaciones/detalle.html", {"votacion": votacion, "voto": voto})


@login_required
@require_http_methods(["GET", "POST"])
def votar(request, categoria_id):
    categoria = get_object_or_404(Categoria.objects.select_related("edicion"), pk=categoria_id)
    contexto = {"categoria": categoria}
    if not categoria.habilitada:
        contexto["error"] = "Esta categoría está cerrada. No se permiten votos."
        return render(request, "votaciones/estado_voto.html", contexto, status=403)
    if Voto.objects.filter(usuario=request.user, categoria=categoria).exists():
        contexto["error"] = "Ya registraste un voto en esta categoría y edición."
        return render(request, "votaciones/estado_voto.html", contexto, status=409)
    form = SeleccionVotoForm(
        request.POST if request.method == "POST" else None,
        categoria=categoria, initial={"opcion": request.GET.get("opcion")},
    )
    contexto["form"] = form
    if request.method == "POST":
        if not form.is_valid():
            return render(request, "votaciones/votar.html", contexto, status=400)
        opcion = form.cleaned_data["opcion"]
        if not form.cleaned_data["confirmar"]:
            contexto["opcion"] = opcion
            return render(request, "votaciones/confirmar_voto.html", contexto)
        try:
            registrar_voto(usuario=request.user, categoria_id=categoria.pk, opcion_id=opcion.pk)
        except VotoDuplicado as exc:
            contexto["error"] = exc.messages[0]
            return render(request, "votaciones/estado_voto.html", contexto, status=409)
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
            return render(request, "votaciones/votar.html", contexto, status=400)
        messages.success(request, "Tu voto se registró correctamente.")
        return redirect("votaciones:participacion")
    return render(request, "votaciones/votar.html", contexto)


@login_required
@require_http_methods(["GET"])
def participacion(request):
    votos = Voto.objects.filter(usuario=request.user).select_related(
        "categoria__edicion", "opcion__votacion",
    )
    return render(request, "votaciones/participacion.html", {"votos": votos})
