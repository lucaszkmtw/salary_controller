from django.contrib import messages, admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import model_ngettext
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin
from celery.worker.control import revoke


from django.contrib.admin.models import DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

admin.site.unregister(TaskResult)


@admin.register(TaskResult)
class CustomTaskResultAdmin(TaskResultAdmin):
    actions = ['cancel_tasks']

    def cancel_tasks(self, request, tasks):
        revoked = revoke(
            'RETRY',
            task_id=[task.task_id for task in tasks],
            terminate=True
        )
        self.message_user(request, revoked, messages.SUCCESS)

    cancel_tasks.short_description = "Cancelar %(verbose_name_plural)s seleccionados/as"

    list_display = TaskResultAdmin.list_display + (('time_delta'),)

    def time_delta(self, obj):
        return obj.date_done - obj.date_created


class CustomModelAdmin(admin.ModelAdmin):
    readonly_fields = [
        'created',
        'modified',
        'deleted',

        'creator',
        'modifier',
        'eliminator',

        'is_active',
    ]
    CUSTOM_ACTIONS = [
        'enable',
        'disable',
    ]
    CONTROL_DATA_FIELDSETS = (
        ('Datos de control', {
            'classes': ('collapse',),
            'fields': (
                'creator',
                'created',

                'modifier',
                'modified',

                'eliminator',
                'deleted',

                'is_active',
            )
        }),
    )

    class Media:
        js = [
            'js/jquery-3.3.1.js',
            'js/list_filter_collapse.js'
        ]

    def get_queryset(self, request):
        """Query para la vista, si es superusuario,
        lista todos los objetos, si es usuario comun
        filtra, y muestra solo los que tienen
        is_active = True.
        """
        if request.user.is_superuser:
            qs = self.model.all_objects
        else:
            qs = self.model.objects

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def save_model(self, request, obj, form, change):
        """Interviene en el save del objeto, si es un
        create le agrega el usuario del request, si es
        un update le agrega el modifier y la fecha.
        """
        if not obj.pk:
            obj.creator = request.user
        else:
            if len(form.changed_data) > 0:
                obj.modifier = request.user
                obj.modified = now()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Interviene el on_save de los inlines
        en este caso cuando va a guardar los inlines
        de movimiento les agrega el request user.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.creator = request.user
            else:
                if len(formset.changed_objects) > 0:
                    instance.modifier = request.user
                    instance.modified = now()
            instance.save()

        formset.save_m2m()

    def changeform_view(self, request, *args, **kwargs):
        """ Arma la vista, si no es superuser le quita
        la opcion de desactivar los objetos.
        """
        self.readonly_fields = list(self.readonly_fields)
        if request.user.is_superuser:
            if 'is_active' in self.readonly_fields:
                self.readonly_fields.remove('is_active')
        return super(CustomModelAdmin, self).changeform_view(request, *args, **kwargs)

    def enable(self, request, queryset):
        """ Cambia a los seleccionados is_active to True
        """
        updated = queryset.update(is_active='True')
        self.message_user(
            request,
            _(
                "Successfully enabled %(count)d %(items)s."
            ) % {
                "count": updated, "items": model_ngettext(self.opts, updated)
            },
            messages.SUCCESS)
    enable.short_description = _("Enable selected %(verbose_name_plural)s")

    def disable(self, request, queryset):
        """ Cambia a los seleccionados is_active to False
        """
        updated = queryset.update(is_active='False')
        self.message_user(
            request,
            _(
                "Successfully disabled %(count)d %(items)s."
            ) % {
                "count": updated, "items": model_ngettext(self.opts, updated)
            },
            messages.SUCCESS)
    disable.short_description = _("Disable selected %(verbose_name_plural)s")


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        '_object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def _object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)
