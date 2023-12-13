import datetime

from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin

from django.contrib import admin
from django.shortcuts import render

from aumentos.models import Proyecto
from aumentos.models import Movimiento
from aumentos.models import Aumento
from aumentos.forms import GenerateAumentos


from main.admin import CustomModelAdmin


class MovimientoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Movimiento
    extra = 0
    fields = [
        'tipo_movimiento', 'reparticion',
        'periodo_dd', 'periodo_ht', 'is_active', 'is_close',
    ]
    order_by = [
        'reparticion', 'orden',
        'periodo_dd', 'periodo_ht'
    ]

    class Media:
        js = ('admin/js/movimiento_inline.js',)


@admin.register(Proyecto)
class ProyectoAdmin(CustomModelAdmin):
    model = Proyecto
    ordering = ['fecha_hiscar', 'fecha_limite']
    list_display = [
        'nombre',
        'descripcion',
        '_fecha_hiscar',
        'fecha_limite',
        'is_close',
        'is_active',
    ]
    fieldsets = (
        (
            'Proyecto',
            {
                'fields': (
                    'nombre',
                    'descripcion',
                    'fecha_hiscar',
                    'fecha_limite',
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    inlines = [MovimientoInline]
    actions = CustomModelAdmin.CUSTOM_ACTIONS

    def save_model(self, request, obj, form, change):
        if obj.fecha_hiscar:  # Setteo al dia 1 del mes
            d = obj.fecha_hiscar
            obj.fecha_hiscar = datetime.datetime(d.year, d.month, 1)
        super().save_model(request, obj, form, change)

    def _fecha_hiscar(self, obj):
        if obj.fecha_hiscar:
            return obj.fecha_hiscar.strftime('%Y-%m')
        else:
            return '-'
    _fecha_hiscar.admin_order_field = 'fecha_hiscar'
    _fecha_hiscar.short_description = 'Fecha Hiscar'


class AumentoInLine(SortableInlineAdminMixin, admin.TabularInline):
    model = Aumento
    extra = 0
    exclude = ['nuevo_cargo', 'has_modulo']
    autocomplete_fields = ['cargo', 'agrupamiento']

    class Media:
        js = ('admin/js/movimiento_inline.js',)


@admin.register(Movimiento)
class MovimientoAdmin(SortableAdminMixin, CustomModelAdmin):
    #  from .forms import MovimientoMonthForm
    #  form = MovimientoMonthForm  # FIXME si se puede hacer asi joya
    model = Movimiento
    ordering = [
        'orden',
    ]
    list_display = [
        'nombre',
        'proyecto',
        'reparticion',
        'tipo_movimiento',
        'periodo_dd',
        'periodo_ht',
        'observaciones',
        'is_close',
    ]
    fieldsets = (
        (
            'Movimiento',
            {
                'fields': (
                    'nombre',
                    'proyecto',
                    'reparticion',
                    'tipo_movimiento',
                    'periodo_dd',
                    'periodo_ht',
                    'observaciones',
                    'is_close',
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    inlines = [AumentoInLine]
    list_filter = ['is_close', 'proyecto']
    autocomplete_fields = ['reparticion']
    actions = ['generar_aumento'] \
        + CustomModelAdmin.CUSTOM_ACTIONS

    def generar_aumento(self, request, movimientos):
        if 'apply' in request.POST:
            return Movimiento.generar_aumentos(movimientos)

        else:
            return render(
                request,
                "admin/aumentos_generar.html",
                {
                    'items': movimientos,
                    'form': GenerateAumentos(
                        initial={
                            '_selected_action': movimientos.values_list('id', flat=True)
                        }
                    )
                }
            )
    generar_aumento.short_description = "Generar %(verbose_name_plural)s seleccionados/as"

    def _periodo_dd(self, obj):
        if obj.periodo_dd:
            return obj.periodo_dd.strftime('%Y-%m')
        else:
            return '-'
    _periodo_dd.admin_order_field = 'periodo_dd'
    _periodo_dd.short_description = 'Periodo desde'

    def _periodo_ht(self, obj):
        if obj.periodo_ht:
            return obj.periodo_ht.strftime('%Y-%m')
        else:
            return '-'
    _periodo_ht.admin_order_field = 'periodo_ht'
    _periodo_ht.short_description = 'Periodo hasta'
