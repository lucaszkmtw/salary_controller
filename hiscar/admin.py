import os

from django.contrib import messages, admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html_join
from django.shortcuts import render
from django.http import HttpResponseRedirect

from adminsortable2.admin import SortableAdminMixin
from rangefilter.filters import DateRangeFilter
from main.paginator import BigQueryPaginator

from hiscar.models import Reparticion
from hiscar.models import ArchivoHiscar
from hiscar.models import Hiscar
from hiscar.models import Asignacion
from hiscar.models import TipoModulo
from hiscar.models import Cargo
from hiscar.models import AgrupamientoCargo
from hiscar.models import Agrupamiento
from hiscar.models import ArchivoTask


from hiscar.forms import ArchivoHiscarParse
from hiscar.forms import ArchivoHiscarForm

from main.admin import CustomModelAdmin


class CargosInline(admin.TabularInline):
    model = Agrupamiento.cargo.through
    autocomplete_fields = ['cargo']
    readonly_fields = ['created', 'modified']
    extra = 0


@admin.register(Agrupamiento)
class AgrupamientoAdmin(CustomModelAdmin):
    model = Agrupamiento
    fieldsets = (
        (
            'Agrupamiento',
            {
                'fields': (
                    'nombre',
                    'reparticion',
                    # 'cargo',
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    list_display = [
        'nombre',
        'reparticion',
        '_cargos',
        'is_active'
    ]
    search_fields = [
        'nombre',
        'reparticion',
        'cargo',
    ]
    list_filter = ['nombre', 'reparticion']
    advanced_filter_fields = [
        'nombre', 'reparticion',
        ('cargo__codigo', 'Cargos que contiene')
    ]
    order = ['-reparticion__is_active', 'reparticion', 'nombre']
    autocomplete_fields = ['cargo']
    inlines = [CargosInline]

    def _cargos(self, agrupamiento):
        cargos_list = [
            '<a href="/admin/Hiscar/cargo/{}/change/">{}</a>'.format(
                c.id, c.codigo) for c in agrupamiento.cargo.all()
        ]
        if len(cargos_list) > 5:
            cargos_list = cargos_list[:5]
            cargos_list.append('...')
        return mark_safe(cargos_list)


@admin.register(Asignacion)
class AsignacionAdmin(CustomModelAdmin):
    pass


@admin.register(TipoModulo)
class TipoModuloAdmin(CustomModelAdmin):
    fieldsets = (
        (
            'Modulo',
            {
                'fields': (
                    'reparticion',
                    'nombre',
                    'codigo',
                    'is_default'
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    autocomplete_fields = ['reparticion']


class AgrupamientoCargoInline(admin.TabularInline):
    model = AgrupamientoCargo
    extra = 0
    fields = ['agrupamiento', 'created', 'modified', 'is_active']
    readonly_fields = ['agrupamiento', 'created', 'modified']


@admin.register(Cargo)
class CargoAdmin(CustomModelAdmin):
    model = Cargo
    list_display = [
        'codigo',
        'cargo',
        'reparticion',
        '_agrupamientos',
        'is_active',
    ]
    ordering = ['reparticion__is_active', 'reparticion', 'codigo']
    search_fields = ['codigo', 'cargo']
    list_filter = [
        'is_active',
        'reparticion',
    ]
    fieldsets = (
        (
            'Cargo',
            {
                'fields': (
                    'reparticion',
                    'codigo',
                    'cargo'
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    readonly_fields = ['reparticion', 'codigo'] + CustomModelAdmin.readonly_fields
    autocomplete_fields = ['reparticion']
    advanced_filter_fields = ['reparticion', 'cargo', 'codigo', 'is_active']
    inlines = [AgrupamientoCargoInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _agrupamientos(self, cargo):
        agrupamientos = [
            f'<a href="/admin/hiscar/agrupamiento/{ a.id}/change/">{a.agrupamiento}</a>'
            for a in AgrupamientoCargo.objects.filter(cargo_id=cargo.id)
        ]
        return mark_safe(agrupamientos)


@admin.register(Reparticion)
class ReparticionAdmin(CustomModelAdmin):
    model = Reparticion
    ordering = ['-is_active', 'codigo']
    list_display = ['codigo', 'nombre', 'has_modulo', 'is_active']
    list_filter = ['has_modulo', 'is_active']
    search_fields = ['codigo', 'nombre']
    actions = CustomModelAdmin.CUSTOM_ACTIONS


class HiscarInLine(admin.TabularInline):
    model = Hiscar
    extra = 0

    def get_queryset(self, request):
        LIMIT_SEARCH = 10
        queryset = super(HiscarInLine, self).get_queryset(request)
        ids = queryset.values('pk')[:LIMIT_SEARCH]
        qs = Hiscar.objects.filter(pk__in=ids).order_by('-id')
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TaskResultInline(admin.TabularInline):
    model = ArchivoTask
    # readonly_fields = ['task', 'archivo']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ArchivoHiscar)
class ArchivoHiscarAdmin(SortableAdminMixin, admin.ModelAdmin):
    model = ArchivoHiscar
    form = ArchivoHiscarForm
    list_display = [
        '_file_name',
        # '_priority',
        '_peso', '_cant_hiscars', 'fecha',
        'autor', '_task', '_hiscar', '_task_status',
        'parsed', 'priority']
    list_filter = [
        'archivo', 'peso',
        'fecha', 'autor']
    search_fields = ['archivo__startswith', ]
    fields = []
    actions = ['parse_file']
    inlines = [HiscarInLine, TaskResultInline]
    class Media:
        js = (
            'js/local_files.js',
        )



    def tasks(self, instance):
        return format_html_join(
            mark_safe('<br/>'),
            '<a href="/admin/django_celery_results/taskresult/{}/change/">{}</a>',
            [(file_task.id, file_task.task_id) for file_task in instance.task.all()])\
            or mark_safe("<span class='errors'>El archivo no posee tasks</span>")

    def save_model(self, request, archivo_hiscar, form, change):
        try:
            archivo_hiscar.guardarArchivo(
                form.cleaned_data['archivo'],
                request.user
            )
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, str(e))

    def parse_file(self, request, queryset):
        if 'apply' in request.POST:
            if request.POST.get('tipo_archivo') == 'impre':
                for archivo_hiscar in queryset:
                    archivo_hiscar.split_process_hiscar_file(request.user.id)
            elif request.POST.get('tipo_archivo') == 'larga':
                for archivo_hiscar in queryset:
                    archivo_hiscar.split_process_hiscar_file(request.user.id)

            return HttpResponseRedirect(

                request.get_full_path()
            )

        form = ArchivoHiscarParse(
            initial={
                '_selected_action': queryset.values_list(
                    'id',
                    flat=True
                )
            }
        )

        return render(
            request,
            "admin/archivo_hiscar_parse.html",
            {
                'items': queryset,
                'form': form
            }
        )

    parse_file.short_description = "Process %(verbose_name_plural)s seleccionados/as"

    def _priority(self, archivo_hiscar):
        return '{}°'.format(archivo_hiscar.priority)

    def _peso(self, archivo_hiscar):
        def sizeof_fmt(num, suffix='B'):
            for unit in ['', 'K', 'M', 'G']:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, 'Yi', suffix)
        return sizeof_fmt(archivo_hiscar.peso)

    def _cant_hiscars(self, archivo_hiscar):
        tasks = archivo_hiscar.task.all()
        if len(tasks) > 0:
            return tasks[0].result[:10]
        else:
            return 0

    def _file_name(self, archivo_hiscar):
        return os.path.basename(archivo_hiscar.archivo)

    def _task(self, archivo_hiscar):
        tasks = archivo_hiscar.task.all()
        if len(tasks) > 0:
            return mark_safe(
                '<a href="/admin/django_celery_results/taskresult/{}/change/">{}</a>'.format(
                    tasks[0].id,
                    tasks[0].task_name
                )
            )
        else:
            return '-'

    def _hiscar(self, archivo_hiscar):
        return mark_safe(
            '<a href="/admin/hiscar/hiscar/?archivo__id__exact={}">{}</a>'.format(
                archivo_hiscar.id, 'Hiscars'
            )
        )

    def _task_status(self, archivo_hiscar):
        tasks = archivo_hiscar.task.all()
        if len(tasks) > 0:
            return tasks[0].status
        else:
            return '-'


@admin.register(Hiscar)
class HiscarAdmin(CustomModelAdmin):
    model = Hiscar
    readonly_fields = ['archivo']
    list_display = [
        '_periodo', 'reparticion_obj', 'cargo_obj',
        'basico', 'suplemento1', 'suplemento2',
        # 'antiguedad', '_aumento'
        'sumafija1', 'sumafija2', 'sumafija3',
    ]
    list_filter = [
        'is_active',
        ('periodo', DateRangeFilter),
        'archivo',
        'reparticion_obj',
        ('cargo_obj', admin.EmptyFieldListFilter),
    ]
    search_fields = [
        'cargo',
        'reparticion']
    actions = [
        'crear_cargos_y_rep',
    ]
    fieldsets = (
        (
            'Cargo',
            {
                'fields': (
                    'periodo',
                    'cargo_obj',
                    'reparticion_obj',
                    'basico',
                    'suplemento1',
                    'suplemento2',
                    'antiguedad',
                    'sumafija1',
                    'sumafija2',
                    'sumafija3',
                )
            }
        ),
    ) + CustomModelAdmin.CONTROL_DATA_FIELDSETS
    actions = CustomModelAdmin.CUSTOM_ACTIONS
    show_full_result_count = False
    paginator = BigQueryPaginator

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _reparticion_cargo(self, hiscar):
        return hiscar.reparticion + hiscar.cargo

    def _periodo(self, obj):
        if obj.periodo:
            return obj.periodo.strftime('%Y-%m')
        else:
            return '-'

    _periodo.admin_order_field = 'periodo'
    _periodo.short_description = 'Periodo'

    def _aumento(self, hiscar):
        if hiscar.aumento:
            button = f"""
            <th class="field-aumento">
                <a href="/admin/aumentos/movimiento/{ hiscar.aumento.movimiento_id }/change/">
                { hiscar.aumento }
                </a>
            </th>
            """
            return mark_safe(button)
        else:
            return "-"
    _aumento.admin_order_field = 'aumento'
