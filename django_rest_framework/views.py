from django.contrib.auth.models import User

from rest_framework import authentication
from rest_framework import viewsets

from django_rest_framework.serializers import AumentoSerializer
from django_rest_framework.serializers import MovimientoSerializer
from django_rest_framework.serializers import ReparticionSerializer
from django_rest_framework.serializers import ProyectoSerializer
from django_rest_framework.serializers import HiscarSerializer
from django_rest_framework.serializers import UserSerializer
from django_rest_framework.serializers import CuadriculaMovimientoSerializer

from aumentos.models import Proyecto
from aumentos.models import Movimiento
from aumentos.models import Aumento

from hiscar.models import Reparticion
from hiscar.models import Hiscar

from cuadricula.models import CuadriculaMovimiento


class AumentoViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Aumento.objects.all()
    serializer_class = AumentoSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer


class ReparticionesViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Reparticion.objects.all()
    serializer_class = ReparticionSerializer


class ProyectoViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class HiscarViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Hiscar.objects.all().order_by('id')
    serializer_class = HiscarSerializer

    def get_queryset(self):
        request_get = self.request._request.GET.dict()
        if ('cargo' in request_get):
            return self.queryset.filter(cargo=request_get['cargo']).order_by('-periodo')
        else:
            return self.queryset


class CuadriculaMovimientoViewSet(viewsets.ModelViewSet):
    queryset = CuadriculaMovimiento.objects.all()
    serializer_class = CuadriculaMovimientoSerializer
