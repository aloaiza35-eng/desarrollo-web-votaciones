from django.contrib import admin

from .models import Categoria, Edicion, Opcion, Votacion, Voto


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "anio")
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "edicion", "habilitada")
    list_filter = ("edicion", "habilitada")
    search_fields = ("nombre",)
    list_select_related = ("edicion",)

    def get_readonly_fields(self, request, obj=None):
        return ("edicion",) if obj and obj.votos.exists() else ()


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "habilitada")
    list_filter = ("categoria__edicion", "categoria", "habilitada")
    search_fields = ("titulo",)
    list_select_related = ("categoria",)

    def get_readonly_fields(self, request, obj=None):
        tiene_votos = obj and Voto.objects.filter(opcion__votacion=obj).exists()
        return ("categoria",) if tiene_votos else ()


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "votacion")
    list_filter = ("votacion",)
    search_fields = ("nombre",)
    list_select_related = ("votacion",)

    def get_readonly_fields(self, request, obj=None):
        return ("votacion",) if obj and obj.votos.exists() else ()


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "edicion", "categoria_nombre", "subevento", "opcion", "fecha")
    list_filter = ("categoria__edicion", "categoria", "opcion__votacion", "fecha")
    search_fields = ("usuario__username", "categoria__nombre", "opcion__nombre")
    list_select_related = ("usuario", "categoria__edicion", "opcion__votacion")
    readonly_fields = ("usuario", "categoria", "opcion", "fecha")

    @admin.display(description="Edición", ordering="categoria__edicion__anio")
    def edicion(self, obj):
        return obj.categoria.edicion.anio

    @admin.display(description="Categoría", ordering="categoria__nombre")
    def categoria_nombre(self, obj):
        return obj.categoria.nombre

    @admin.display(description="Subevento", ordering="opcion__votacion__titulo")
    def subevento(self, obj):
        return obj.opcion.votacion

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
