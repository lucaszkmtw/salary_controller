from django.http import JsonResponse
import os
from django.conf import settings


def local_files(request):
    FILE_DIRS = settings.MEDIA_ROOT + '/hiscar/'
    HISCAR_FILES = [d for d in os.listdir(FILE_DIRS) if os.path.isfile(os.path.join(FILE_DIRS, d))]
    data = {
        'files': HISCAR_FILES
    }
    return JsonResponse(data)


