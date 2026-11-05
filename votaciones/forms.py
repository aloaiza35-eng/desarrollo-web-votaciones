from django import forms

from .models import Opcion


class OpcionField(forms.ModelChoiceField):
    def label_from_instance(self, opcion):
        return f"{opcion.nombre} — {opcion.votacion.titulo}"


class SeleccionVotoForm(forms.Form):
    opcion = OpcionField(
        queryset=Opcion.objects.none(), widget=forms.RadioSelect,
        label="Selecciona una opción",
        error_messages={
            "required": "Selecciona una opción para continuar.",
            "invalid_choice": "Selecciona una opción válida de un subevento habilitado de esta categoría.",
        },
    )
    confirmar = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, categoria, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opcion"].queryset = Opcion.objects.filter(
            votacion__categoria=categoria, votacion__habilitada=True,
        ).select_related("votacion").order_by("votacion__titulo", "nombre", "pk")
