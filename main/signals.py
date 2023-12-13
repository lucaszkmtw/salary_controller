from django.db.models.signals import m2m_changed, post_save
from main.models import CustomModel


def clear_cache(sender, instance, created, **kwargs):
    print(str(1))  # FIXME falta el signal para clerear el cache


m2m_changed.connect(clear_cache, sender=CustomModel)
post_save.connect(clear_cache, sender=CustomModel)
