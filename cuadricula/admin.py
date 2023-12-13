from django.contrib import admin
from django import forms
from django.forms import Textarea
from django.http import HttpResponse

from main.admin import CustomModelAdmin
from .models import Comment

from cuadricula.models import CuadriculaMovimiento


class CuadriculaMovimientoForm(forms.ModelForm):
    class Meta:
        model = CuadriculaMovimiento
        fields = '__all__'
        widgets = {
            'observaciones': Textarea,
        }


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['text']
    classes = ['collapse']


@admin.register(CuadriculaMovimiento)
class CuadriculaMovimientoAdmin(CustomModelAdmin):
    """CuadriculaMovimientoAdmin

    Args:
        CustomModelAdmin (CustomModelAdmin): custom model for
        admin detailed in Hiscar.admin.
    """
    form = CuadriculaMovimientoForm
    fieldsets = (
        (
            'Tipo de Aumento',
            {
                'fields': (
                    'proyecto',
                    'codigo',
                    ('periodo_dd', 'periodo_ht',),
                    'nombre',
                    'observaciones',
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    list_display = [
        'nombre',
        'codigo',
        '_periodo_desde', '_periodo_hasta',
        'observaciones',
        'creator',
        'is_active',
    ]
    list_filter = [
        'proyecto',
        'codigo',
        'is_active',
    ]
    inlines = [CommentInline]

    actions = [
        'generar_script'
    ] + CustomModelAdmin.CUSTOM_ACTIONS

    def _periodo_desde(self, cuadricula):
        return cuadricula.periodo_dd

    def _periodo_hasta(self, cuadricula):
        return cuadricula.periodo_ht

    def generar_script(self, request, queryset):
        file_data = ''
        for cuadricula in queryset:
            file_data += cuadricula.movimiento_bash()
        response = HttpResponse(file_data, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="Hiscmun.bsh"'
        return response
