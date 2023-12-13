from django import forms
from cuadricula.models import CuadriculaMovimiento


class CuadriculaForm(forms.ModelForm):
    class Meta:
        model = CuadriculaMovimiento
        fields = ['proyecto', 'reparticion', 'nombre', 'codigo',
                  'periodo_dd', 'periodo_ht', 'observaciones', 'creator']
        labels = {
            'Proyecto': 'proyecto',
            'reparticion': 'nombre de la reparticion',
            'nombre': 'nombre del municipio',
            'codigo': 'codigo',
            'periodo_dd': 'periodo desde',
            'periodo_ht': 'periodo hasta',
            'observaciones': 'descripcion',
            'creator': 'creador'
        }
        widgets = {
            'proyecto': forms.SelectMultiple(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese tipo proyecto'
                }
            ),
            'reparticion': forms.SelectMultiple(
                attrs={
                    'class': 'form-control'
                }
            ),
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el nombre'
                }
            ),
            'codigo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el codigo'
                }
            ),
            'periodo_dd': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el periodo desde',
                    'type': 'date',


                }
            ),
            'periodo_ht': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el periodo hasta',
                    'type': 'date',
                }
            ),
            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese una descripcion'
                }
            ),
            'creator': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ingrese el creador',
                    'type': 'hidden'

                }
            )
        }
