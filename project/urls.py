from django.urls import path, include
from django.contrib import admin
from django.conf import settings


from main.views import home


urlpatterns = [
    # Home
    path('', home, name='home'),

    # Django
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Apps
    path('cuadricula/', include('cuadricula.urls')),
    path('aumentos/', include('aumentos.urls')),
    path('', include('hiscar.urls')),
    path('django_rest_framework/', include('django_rest_framework.urls')),

    # Librerías
    path("select2/", include("django_select2.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)), ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
