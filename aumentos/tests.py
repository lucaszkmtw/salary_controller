import datetime

from django.test import TestCase

from aumentos.models import Proyecto
from aumentos.models import Movimiento
from aumentos.models import Aumento

from hiscar.models import Reparticion
from django.contrib.auth.models import User


class ProyectoTest(TestCase):
    def setUp(self):
        """Crear proyecto -> movimiento -> aumento 30%."""
        usuario = User.objects.create_user('pepe', 'pepe@pepemail.com', 'pepasword')
        reparticion = Reparticion.objects.create(
            codigo='PEPITO',
            nombre='REPUBLICA PEPITO',
            creator=usuario
        )
        test_proyecto = Proyecto.objects.create(
            nombre="TEST",
            descripcion="TEST1",
            fecha_limite=datetime.datetime.strptime('2021-04', "%Y-%m").date(),
            fecha_hiscar=datetime.datetime.strptime('2021-04-29', "%Y-%m-%d").date(),
            creator=usuario
        )
        test_movimiento = Movimiento.objects.create(
            creator=usuario,
            periodo_dd=datetime.datetime.strptime('2021-03', "%Y-%m").date(),
            periodo_ht=datetime.datetime.strptime('2021-04', "%Y-%m").date(),
            nombre='TEST MOVIMIENTO 1',
            reparticion=reparticion,
            tipo_movimiento=Movimiento.TIPOS_MOVIMIENTOS[0][0],
            proyecto=test_proyecto,
            orden=1,
        )
        test_aumento = Aumento.objects.create(
            movimiento=test_movimiento,
            regla='S2%',
            valor=30,
            orden=1
        )
        test_aumento.save()

    def test_creacion_aumento(self):
        test_aumento = Aumento.objects.get(id=1)
        self.assertEqual(test_aumento.valor, 30)
