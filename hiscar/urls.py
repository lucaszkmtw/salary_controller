


from hiscar.views import local_files
from django.urls import path

urlpatterns = [
    # Proyecto
    path('local_files/', local_files, name='local_files'),
    ]