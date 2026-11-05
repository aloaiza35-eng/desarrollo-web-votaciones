from django.urls import path
from . import views

app_name = "votaciones"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("ediciones/", views.ediciones, name="ediciones"),
    path("ediciones/<int:edicion_id>/", views.categorias, name="categorias"),
    path("categorias/<int:categoria_id>/", views.votaciones, name="votaciones"),
    path("categorias/<int:categoria_id>/votar/", views.votar, name="votar"),
    path("votaciones/<int:votacion_id>/", views.detalle, name="detalle"),
    path("mi-participacion/", views.participacion, name="participacion"),
]
