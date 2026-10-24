from django.db import models

# Propuestas preliminares del equipo, no reglas aprobadas del cliente:
# - Una edición por año.
# - Nombre de categoría único dentro de una edición.
# - Protección de eliminación de registros con elementos asociados.


class Edicion(models.Model):
    nombre = models.CharField(max_length=150)
    anio = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        verbose_name = "edición"
        verbose_name_plural = "ediciones"
        ordering = ["-anio"]

    def __str__(self):
        return f"{self.nombre} ({self.anio})"


class Categoria(models.Model):
    edicion = models.ForeignKey(
        Edicion,
        on_delete=models.PROTECT,
        related_name="categorias",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["edicion", "nombre"],
                name="categoria_nombre_por_edicion",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.edicion}"


class Votacion(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="votaciones",
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "votación"
        verbose_name_plural = "votaciones"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class Opcion(models.Model):
    votacion = models.ForeignKey(
        Votacion,
        on_delete=models.PROTECT,
        related_name="opciones",
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "opción"
        verbose_name_plural = "opciones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
