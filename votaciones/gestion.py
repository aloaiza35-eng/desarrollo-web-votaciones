"""Interfaz de gestión para personal autorizado del festival."""
import csv
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .gestion_forms import CategoriaForm, EdicionForm, OpcionForm, VotacionForm
from .models import Categoria, Edicion, Opcion, Votacion, Voto

TIPOS = {
    "ediciones": (Edicion, EdicionForm, "Ediciones", "edición"),
    "categorias": (Categoria, CategoriaForm, "Categorías", "categoría"),
    "subeventos": (Votacion, VotacionForm, "Subeventos", "subevento"),
    "opciones": (Opcion, OpcionForm, "Opciones", "opción"),
}


def personal(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied("Esta sección es solo para personal autorizado.")
        return view(request, *args, **kwargs)
    return wrapped


def config(tipo):
    try:
        return TIPOS[tipo]
    except KeyError:
        raise Http404("Sección inexistente") from None


def contexto(tipo):
    modelo, form, titulo, singular = config(tipo)
    return {"tipo": tipo, "titulo": titulo, "singular": singular, "modelo": modelo, "clase_form": form}


@personal
@require_GET
def inicio(request):
    return render(request, "gestion/inicio.html", {"total_votos": Voto.objects.count()})


@personal
@require_GET
def listado(request, tipo):
    ctx = contexto(tipo)
    consulta = ctx["modelo"].objects.all()
    relaciones = {"categorias": "edicion", "subeventos": "categoria__edicion", "opciones": "votacion__categoria__edicion"}
    if tipo in relaciones:
        consulta = consulta.select_related(relaciones[tipo])
    ctx["registros"] = consulta.order_by("-activo", "pk")
    return render(request, "gestion/listado.html", ctx)


@personal
@require_http_methods(["GET", "POST"])
def editar(request, tipo, pk=None):
    ctx = contexto(tipo)
    instancia = get_object_or_404(ctx["modelo"], pk=pk) if pk is not None else None
    formulario = ctx["clase_form"](request.POST if request.method == "POST" else None, instance=instancia)
    if request.method == "POST" and formulario.is_valid():
        try:
            with transaction.atomic():
                formulario.save()
        except IntegrityError:
            formulario.add_error(None, "No se pudo guardar: ya existe un registro con esos datos o la relación cambió. Revísalos e inténtalo de nuevo.")
        else:
            messages.success(request, f"La {ctx['singular']} se guardó correctamente." if tipo != "subeventos" else "El subevento se guardó correctamente.")
            return redirect("gestion:listado", tipo=tipo)
    ctx.update(form=formulario, instancia=instancia)
    return render(request, "gestion/formulario.html", ctx)


@personal
@require_http_methods(["GET", "POST"])
def archivar(request, tipo, pk):
    ctx = contexto(tipo)
    obj = get_object_or_404(ctx["modelo"], pk=pk)
    if request.method == "POST":
        obj.activo = False
        obj.save(update_fields=["activo"])
        messages.success(request, "Registro archivado. Se conserva en la base de datos y puede restaurarse.")
        return redirect("gestion:listado", tipo=tipo)
    ctx["registro"] = obj
    return render(request, "gestion/archivar.html", ctx)


@personal
@require_POST
def restaurar(request, tipo, pk):
    ctx = contexto(tipo)
    obj = get_object_or_404(ctx["modelo"], pk=pk)
    obj.activo = True
    obj.save(update_fields=["activo"])
    messages.success(request, "Registro restaurado. Si pertenece a otro registro archivado, restaura también su registro superior.")
    return redirect("gestion:listado", tipo=tipo)


@personal
@require_GET
def votos(request):
    registros = Voto.objects.select_related("usuario", "categoria__edicion", "opcion__votacion")
    return render(request, "gestion/votos.html", {"votos": registros})


def estadisticas():
    return Categoria.objects.select_related("edicion").annotate(
        total_votos=Count("votos", distinct=True),
        opciones_activas=Count("votaciones__opciones", filter=Q(votaciones__activo=True, votaciones__opciones__activo=True), distinct=True),
    ).order_by("-edicion__anio", "nombre", "pk")


@personal
@require_GET
def informe(request):
    return render(request, "gestion/informe.html", {"categorias": estadisticas()})


def csv_seguro(valor):
    valor = str(valor)
    return "'" + valor if valor.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else valor


@personal
@require_GET
def informe_csv(request):
    respuesta = HttpResponse(content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = 'attachment; filename="informe_participacion.csv"'
    respuesta.write("\ufeff")
    writer = csv.writer(respuesta)
    writer.writerow(["Edición", "Año", "Categoría", "Estado del registro", "Votación habilitada", "Opciones activas", "Votos registrados"])
    for categoria in estadisticas():
        writer.writerow([csv_seguro(categoria.edicion.nombre), categoria.edicion.anio, csv_seguro(categoria.nombre),
                         "Activa" if categoria.activo else "Archivada", "Sí" if categoria.habilitada else "No",
                         categoria.opciones_activas, categoria.total_votos])
    return respuesta
