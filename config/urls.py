from django.contrib import admin
from django.urls import include, path
from votaciones import api

urlpatterns = [
    path("gestion/", include("votaciones.gestion_urls")),
    path("admin/", admin.site.urls),
    path("cuentas/", include("cuentas.urls")),
    path("api/categorias/", api.categorias, name="api_categorias"),
    path("", include("votaciones.urls")),
]
