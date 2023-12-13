from collections import defaultdict

from django.apps import apps
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.core.cache import cache


class CustomModelManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.active_only = kwargs.pop('active_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.active_only:
            return super().get_queryset().filter(is_active=True)
        return super().get_queryset()


class CustomModel(models.Model):
    created    = models.DateTimeField(default=now)
    modified   = models.DateTimeField(default=None, null=True, blank=True)
    deleted    = models.DateTimeField(default=None, null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    creator    = models.ForeignKey(settings.AUTH_USER_MODEL,
                 on_delete=models.DO_NOTHING,
                 related_name=_("%(class)s_creator"))
    modifier   = models.ForeignKey(settings.AUTH_USER_MODEL,
                 default=None,
                 null=True,
                 blank=True,
                 on_delete=models.DO_NOTHING,
                 related_name=_("%(class)s_modifier"))
    eliminator = models.ForeignKey(settings.AUTH_USER_MODEL,
                 default=None,
                 null=True,
                 blank=True,
                 on_delete=models.DO_NOTHING,
                 related_name=_("%(class)s_eliminator"))

    objects = CustomModelManager()
    all_objects = CustomModelManager(active_only=False)

    class Meta:
        abstract = True
        managed  = False

    def delete(self):
        self.is_active = False
        self.deleted = now()
        self.save()

    def hard_delete(self):
        super(CustomModel, self).delete()

    @classmethod
    def get_by_cache(self, **kwargs):
        key = '.'.join([self.__name__] + [f'{arg}={val}' for arg, val in kwargs.items()])
        if not kwargs:
            query = self.objects.all()
        else:
            query = self.objects.filter(**kwargs)
        return cache.get_or_set(key, query, timeout=300)



class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))
