from django.conf import settings
from django.core.exceptions import ValidationError
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
    habilitada = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.pk and self.votos.exists():
            anterior = type(self).objects.get(pk=self.pk)
            if self.edicion_id != anterior.edicion_id:
                raise ValidationError({"edicion": "Una categoría con votos no puede cambiar de edición."})

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
    habilitada = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.pk and Voto.objects.filter(opcion__votacion_id=self.pk).exists():
            anterior = type(self).objects.get(pk=self.pk)
            if self.categoria_id != anterior.categoria_id:
                raise ValidationError({"categoria": "Un subevento con votos no puede cambiar de categoría."})

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

    def clean(self):
        super().clean()
        if self.pk and self.votos.exists():
            anterior = type(self).objects.get(pk=self.pk)
            if self.votacion_id != anterior.votacion_id:
                raise ValidationError({"votacion": "Una opción con votos no puede cambiar de subevento."})

    class Meta:
        verbose_name = "opción"
        verbose_name_plural = "opciones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Voto(models.Model):
    """La edición se obtiene de categoria.edicion, sin duplicar esa relación.

    Cada categoría pertenece a una sola edición. UNIQUE(usuario, categoria)
    garantiza un voto por categoría y edición, incluso entre subeventos.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="votos",
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="votos",
    )
    opcion = models.ForeignKey(
        Opcion, on_delete=models.PROTECT, related_name="votos",
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-pk"]
        verbose_name = "voto"
        verbose_name_plural = "votos"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "categoria"], name="voto_unico_usuario_categoria",
            ),
        ]

    @property
    def edicion(self):
        return self.categoria.edicion

    def clean(self):
        super().clean()
        if self.pk and not self._state.adding:
            raise ValidationError("Los votos registrados no se pueden modificar.")
        if self.categoria_id and self.opcion_id:
            if self.opcion.votacion.categoria_id != self.categoria_id:
                raise ValidationError({"opcion": "La opción no pertenece a esta categoría y edición."})
            if not self.categoria.habilitada:
                raise ValidationError({"categoria": "Esta categoría está cerrada."})
            if not self.opcion.votacion.habilitada:
                raise ValidationError({"opcion": "Este subevento está cerrado."})

    def save(self, *args, **kwargs):
        # La unicidad se impone en la BD, también si dos solicitudes compiten.
        # full_clean() aporta validación de pertenencia a las escrituras ORM normales.
        self.full_clean(validate_unique=False, validate_constraints=False)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} · {self.categoria} · {self.opcion}"
