from django.contrib import admin

from .models import Categoria, Edicion, Opcion, Votacion


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "anio")
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "edicion")
    list_filter = ("edicion",)
    search_fields = ("nombre",)
    list_select_related = ("edicion",)


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria")
    list_filter = ("categoria__edicion", "categoria")
    search_fields = ("titulo",)
    list_select_related = ("categoria",)


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "votacion")
    list_filter = ("votacion",)
    search_fields = ("nombre",)
    list_select_related = ("votacion",)
