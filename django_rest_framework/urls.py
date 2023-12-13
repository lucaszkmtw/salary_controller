from django.urls import include, path
from rest_framework import routers

from django_rest_framework.views import ProyectoViewSet
from django_rest_framework.views import UserViewSet
from django_rest_framework.views import ReparticionesViewSet
from django_rest_framework.views import MovimientoViewSet
from django_rest_framework.views import HiscarViewSet
from django_rest_framework.views import AumentoViewSet
from django_rest_framework.views import CuadriculaMovimientoViewSet


router = routers.DefaultRouter()

router.register(r'proyectos', ProyectoViewSet, basename='drf-proyecto')
router.register(r'users', UserViewSet, basename='drf-user')
router.register(r'reparticiones', ReparticionesViewSet, basename='drf-reparticion')
router.register(r'movimientos', MovimientoViewSet, basename='drf-movimiento')
router.register(r'aumentos', AumentoViewSet, basename='drf-aumento')
router.register(r'hiscar', HiscarViewSet, basename='drf-hiscar')
router.register(r'cuadricula', CuadriculaMovimientoViewSet, basename='drf-cuadricula')


urlpatterns = [
    path('', include(router.urls)),
]
