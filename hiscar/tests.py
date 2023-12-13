from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from hiscar.models import Hiscar, Reparticion

TestCase.maxDiff = None


class ParseLineTest(TestCase):
    fixtures = [
        'users.json',
        'reparticiones.json']

    LINE_ANTIGUEDAD = "202107M073S051000000000008958140000000000000000000000000" + \
                      "00000000000000179162000003583250000053748800000716651000" + \
                      "00895814000010749760000125413900001433302000016124650000" + \
                      "17916280000197079000002149953000023291160000250827900002" + \
                      "68744200002866604000030457670000322493000003404093000035" + \
                      "83256000037624180000394158100004120744000042999070000447" + \
                      "90700000465823200004837395000050165580000519572100005374" + \
                      "88400005554046000057332090000591237200006091535000062706" + \
                      "98000064498600000662902300006808186000069873490000716651" + \
                      "20000000000000000000000008958140"

    maxDiff = None

    def setUp(self):
        hiscar = Hiscar()
        hiscar.parse_line_vec_antiguedad(self.LINE_ANTIGUEDAD)
        hiscar.reparticion_obj = Reparticion.objects.get(codigo='M073')
        hiscar.creator = User.objects.get(id=2)
        hiscar.save()

    def test_can_parse_hiscar_line(self):
        hiscar = Hiscar.objects.get(id=1)
        periodo = datetime.strptime('202107', '%Y%m')
        hiscar_line = hiscar.generate_line_vec_antiguedad(periodo)
        self.assertEqual(len(hiscar_line), len(self.LINE_ANTIGUEDAD))
        self.assertEqual(hiscar_line, self.LINE_ANTIGUEDAD)
