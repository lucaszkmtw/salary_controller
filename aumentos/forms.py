from django import forms
from .models import Movimiento


class GenerateAumentos(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class MovimientoMonthForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        widgets = {
            'periodo_dd': forms.TextInput(attrs={
                'type': 'month'
            }),
            'periodo_ht': forms.TextInput(attrs={
                'type': 'month',
                'value': '%Y-%m-%d'
            })
        }
        fields = '__all__'
