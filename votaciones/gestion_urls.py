from django.urls import path
from . import gestion

app_name = "gestion"
urlpatterns = [
    path("", gestion.inicio, name="inicio"),
    path("votos/", gestion.votos, name="votos"),
    path("informe/", gestion.informe, name="informe"),
    path("informe/descargar/", gestion.informe_csv, name="informe_csv"),
    path("<str:tipo>/", gestion.listado, name="listado"),
    path("<str:tipo>/crear/", gestion.editar, name="crear"),
    path("<str:tipo>/<int:pk>/editar/", gestion.editar, name="editar"),
    path("<str:tipo>/<int:pk>/archivar/", gestion.archivar, name="archivar"),
    path("<str:tipo>/<int:pk>/restaurar/", gestion.restaurar, name="restaurar"),
]
