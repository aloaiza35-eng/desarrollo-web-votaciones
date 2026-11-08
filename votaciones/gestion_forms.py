from django import forms
from .models import Categoria, Edicion, Opcion, Votacion


class EdicionForm(forms.ModelForm):
    class Meta:
        model = Edicion
        fields = ("nombre", "anio")
        labels = {"anio": "Año"}


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("edicion", "nombre", "descripcion", "habilitada")
        labels = {"edicion": "Edición", "descripcion": "Descripción", "habilitada": "Habilitada para votar"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class VotacionForm(forms.ModelForm):
    class Meta:
        model = Votacion
        fields = ("categoria", "titulo", "descripcion", "habilitada")
        labels = {"categoria": "Categoría", "titulo": "Título", "descripcion": "Descripción", "habilitada": "Habilitado para votar"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ("votacion", "nombre", "descripcion")
        labels = {"votacion": "Subevento", "descripcion": "Descripción"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}
