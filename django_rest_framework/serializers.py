from django.contrib.auth.models import User
from aumentos.models import Proyecto
from aumentos.models import Movimiento
from aumentos.models import Aumento

from hiscar.models import Hiscar
from hiscar.models import Reparticion

from cuadricula.models import CuadriculaMovimiento

from rest_framework import serializers


class HiscarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hiscar
        ordering = ['-id']
        fields = [
            'periodo',
            'cargo',
            'reparticion',
            'basico',
            'suplemento1',
            'suplemento2',
            'antiguedad',
            'sumafija1',
            'sumafija2',
            'sumafija3'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ProyectoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proyecto
        fields = [
            'id', 'nombre',
            'descripcion', 'fecha_limite',
        ]


class ReparticionSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    def get_DT_RowId(self, reparticion):
        return 'row-' + str(reparticion.id)

    def get_DT_RowAttr(self, reparticion):
        style = ''
        if not reparticion.is_active:
            style = "text-decoration: line-through!important;color:#CCC"
        return {'name': reparticion.nombre, 'style': style}

    class Meta:
        model = Reparticion
        fields = '__all__'


class MovimientoSerializer(serializers.HyperlinkedModelSerializer):
    proyecto = ProyectoSerializer(read_only=True)
    reparticion = ReparticionSerializer(read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            'id', 'descripcion',
            'tipo_movimiento', 'reparticion',
            'orden', 'proyecto',
            'is_close'
        ]


class AumentoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Aumento
        fields = '__all__'


class ReparticionSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Reparticion
        fields = (
            'codigo',
            'nombre'
        )


class CuadriculaMovimientoSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    reparticion = ReparticionSerializerV2()

    class Meta:
        model = CuadriculaMovimiento
        fields = (
            'id',
            'codigo',
            'nombre',
            'reparticion',
            'periodo_dd',
            'periodo_ht',
            'creator',
        )
