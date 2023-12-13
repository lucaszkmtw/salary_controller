import os

from os import path

from django import forms
from django.conf import settings

from hiscar.models import ArchivoHiscar

from django.core.files.storage import default_storage

FILE_DIRS = settings.MEDIA_ROOT + '/hiscar/'
NONE_CHOICE = [(None, '-' * 20)]



class ArchivoHiscarParse(forms.Form):
    tipo_archivo = forms.CharField(
        label="Tipo de archivo",
        widget=forms.Select(
            choices=(
                ('larga', 'Con antiguedad'),
                ('impre', 'Solo impre'),
            )
        ),
        required=True
    )
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class ArchivoHiscarForm(forms.ModelForm):
    class Meta:
        model = ArchivoHiscar
        fields = []

    archivo_externo = forms.FileField(
        label="Archivo externo",
        required=False
    )
    archivo_local = forms.CharField(
        label="Archivo local",
        widget=forms.Select(
            choices=(NONE_CHOICE)
        ),
        required=False

    )

    def clean(self):
        archivo_local = self.cleaned_data['archivo_local']
        archivo_externo = self.cleaned_data['archivo_externo']

        if archivo_externo:
            with default_storage.open(FILE_DIRS + archivo_externo.name, 'wb+') as f:
                for chunk in archivo_externo.chunks():
                    f.write(chunk)
            if not path.exists(FILE_DIRS + archivo_externo.name):
                self.add_error('archivo_externo', f'{archivo_externo.name} does not exist in {FILE_DIRS}.')
            else:
                self.cleaned_data['archivo'] = FILE_DIRS + archivo_externo.name

        elif archivo_local:
            if not path.exists(FILE_DIRS + archivo_local):
                self.add_error('archivo_local', f'{archivo_local} does not exist in {FILE_DIRS}.')
            else:
                self.cleaned_data['archivo'] = FILE_DIRS + archivo_local

        else:
            self.add_error(None, 'Debe seleccionar al menos un archivo local o subir uno')
