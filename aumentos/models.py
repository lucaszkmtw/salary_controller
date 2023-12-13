from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.urls.base import reverse

from main.models import CustomModel

from cuadricula.models import CuadriculaMovimiento

from hiscar.models import Cargo
from hiscar.models import Agrupamiento
from hiscar.models import Hiscar


class Proyecto(CustomModel):
    nombre       = models.CharField(max_length=60, default=None, null=True)
    descripcion  = models.CharField(max_length=120, default=None, null=True)
    fecha_limite = models.DateField(null=True)
    fecha_hiscar = models.DateField(null=True)
    is_close     = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'proyectos'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.nombre + ' ' + self.descripcion

    def get_absolute_url(self):
        return reverse('proyecto-create')

    def get_movimientos(self):
        return Movimiento.objects\
            .filter(is_active=True, proyecto_id=self.id)\
            .select_related('reparticion')\
            .order_by('orden')


class Movimiento(CuadriculaMovimiento):
    """
    codigo
    periodo_dd
    periodo_ht
    nombre
    observaciones
    proyecto
    reparticion
    tipo_movimiento
    orden
    is_close
    """
    TIPOS_MOVIMIENTOS = (
        (1, 'Aumento'),
        (2, 'Alta'),
        (3, 'Baja')
    )

    tipo_movimiento = models.IntegerField(
                      choices=TIPOS_MOVIMIENTOS,
                      default=TIPOS_MOVIMIENTOS[0][0])
    orden           = models.IntegerField(blank=True, null=True)
    is_close        = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'movimientos'
        ordering = ['orden']
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'

    def __str__(self):
        return f"[{self.id}] {self.nombre}"

    def get_absolute_url(self):
        return reverse('movimiento-create')

    def get_periodo_desde(self):
        return self.periodo_dd.strftime('%Y-%m')

    def get_periodo_hasta(self):
        return self.periodo_ht.strftime('%Y-%m')

    def new_update(periodo_dd, periodo_ht, observaciones, reparticion,
                   usuario, aume_id, proyecto, orden, tipo_movimiento):
        if not aume_id or not Movimiento.objects.filter(id=aume_id).exists():
            aume = Movimiento(
                periodo_dd=periodo_dd,
                periodo_ht=periodo_ht,
                observaciones=observaciones,
                reparticion=reparticion,
                creator=usuario,
                proyecto=proyecto,
                tipo_movimiento=tipo_movimiento,
                orden=orden)

            aume.save()
            return aume.id
        else:
            Movimiento.objects\
                .filter(id=aume_id)\
                .update(
                    periodo_dd=periodo_dd,
                    periodo_ht=periodo_ht,
                    observaciones=observaciones,
                    reparticion=reparticion,
                    creator=usuario)

    def getHiscar(self):
        return Aumento.getHiscars(self.id, self.periodo_dd)

    def generar_aumentos(movimientos):
        query = Q()
        content = ''
        hiscar_aumentos = []
        movimientos_ids = [m.id for m in movimientos]
        tipos_aumentos = dict(Aumento.TIPOS_AUMENTOS)
        tipos_calculos = dict(Aumento.TIPOS_CALCULOS)

        # Obtengo los aumentos de los movimientos.
        aumentos = Aumento.objects.filter(movimiento_id__in=[m.id for m in movimientos]).order_by('orden')
        Hiscar.objects.filter(aumento_id__in=[a.id for a in aumentos]).delete()

        # Obtengo la query para filtrar reparticiones entre periodos
        periodos_reparticion_tup = [(m.periodo_dd, m.periodo_ht, m.reparticion.codigo) for m in movimientos]
        for pr in periodos_reparticion_tup:
            query.add(
                Q(
                    periodo__gte=pr[0],
                    periodo__lte=pr[1],
                    reparticion=pr[2]
                ),
                Q.OR
            )

        # Obtengo las hiscars filtrando por la query
        h = Hiscar.objects.\
            filter(query, archivo__isnull=False).\
            order_by(
                'periodo',
                'reparticion',
                'cargo').\
            all()

        #  Aplicar aumentos
        for movimiento in movimientos:
            hiscars = h.filter(periodo=movimiento.periodo_dd)
            for aumento in aumentos.filter(movimiento=movimiento):
                for hisc in hiscars.filter(aumento._get_hiscars_filter()):
                    sueldo = float(getattr(hisc, tipos_calculos[aumento.tipo_calculo]))

                    if tipos_aumentos[aumento.tipo_aumento] == 'Porcentaje':
                        monto_aumento = sueldo * float(aumento.valor) / 100
                    else:
                        monto_aumento = float(aumento.valor)

                    nuevo_sueldo = sueldo + monto_aumento
                    setattr(hisc, tipos_calculos[aumento.tipo_calculo], nuevo_sueldo)

                    hisc.pk = None
                    hisc.archivo = None
                    hisc.periodo = None
                    hisc.aumento = aumento
                    hiscar_aumentos.append(hisc)

        id_for_exc = []

        for he in hiscar_aumentos:
            nh = h.filter(
                cargo=he.cargo,
                reparticion=he.reparticion,
                archivo__isnull=False
            )
            for n in nh:
                he.periodo = n.periodo
                he.save()
                id_for_exc.append(n.id)

        nuevas_hiscars = Hiscar.objects.\
            filter(query, periodo=movimiento.periodo_dd).\
            exclude(id__in=id_for_exc).\
            order_by(
                'periodo',
                'reparticion',
                'cargo').\
            all()

        print(len(nuevas_hiscars.filter(archivo__isnull=True)))

        # ULTRA FIXME
        content += "   INSTITUTO DE PREVISION SOCIAL" + " " * 82 + "HOJA NRO.      1" + '\n'
        content += """   PGM: LISTHISC   EJECUTADO EL 25/07/2021A LAS  16:19:46  HS""" + '\n'
        content += """                   ACTUALIZACION AL MAESTRO HISTORICO DE CARGOS""" + '\n'
        content += '\n'
        content += """ AAAA MM     CODIGO          BASICO         SUPL1     SUPL2        ANTIG      SUMAFIJ1       SUMAFIJ2           SUMAFIJ3""" + '\n'

        for hh in nuevas_hiscars:
            content += hh.generate_line(movimiento.periodo_dd) + '\n'

        response = HttpResponse(content, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = f"attachment; filename=movimientos{'_'.join(str(movimientos_ids))}.txt"
        return response


class Aumento(models.Model):
    """Modelo de Aumento.

    Arguments:
        models {aumento} -- Los aumentos son las
        operaciones que constituyen al movimiento

    Returns:
        object -- objeto(
            movimiento,
            tipo_aumento,
            tipo_calculo,
            cargo,
            agrupamiento,
            regla,
            valor,
            orden,
            has_modulo)
    """

    TIPOS_CALCULOS = (
        (1, 'basico'),
        (2, 'suplemento1'),
        (3, 'suplemento2'),
        (4, 'sumafija1'),
        (5, 'sumafija2'),
        (6, 'sumafija3'),
    )

    TIPOS_AUMENTOS = (
        (1, 'Porcentaje'),
        (2, 'Suma Fija'),
    )

    movimiento   = models.ForeignKey(
                   Movimiento,
                   on_delete=models.CASCADE,
                   blank=True,
                   null=True)
    tipo_aumento = models.IntegerField(
                   choices=TIPOS_AUMENTOS,
                   default=TIPOS_AUMENTOS[0][0])
    tipo_calculo = models.IntegerField(
                   choices=TIPOS_CALCULOS,
                   default=TIPOS_CALCULOS[0][0])
    cargo        = models.ForeignKey(
                   Cargo,
                   on_delete=models.CASCADE,
                   blank=True,
                   null=True)
    agrupamiento = models.ForeignKey(
                   Agrupamiento,
                   on_delete=models.CASCADE,
                   blank=True,
                   null=True)
    regla        = models.CharField(
                   max_length=256,
                   default=None,
                   blank=True,
                   null=True)
    valor        = models.DecimalField(
                   max_digits=18,
                   decimal_places=2,
                   blank=True,
                   null=True)
    orden        = models.IntegerField(
                   blank=True,
                   null=True)
    has_modulo   = models.BooleanField(
                   default=False)

    class Meta:
        db_table = 'aumentos'
        ordering = ['orden']

    def __str__(self):
        if self.TIPOS_CALCULOS[self.tipo_calculo] == 'Porcentaje':
            return '%{}->{}'.format(self.valor, self.TIPOS_CALCULOS[self.tipo_calculo])
        else:
            return '+{}->{}'.format(self.valor, self.TIPOS_CALCULOS[self.tipo_calculo])

    def modo_aumento(self):
        if self.cargo:
            return 'cargo'
        elif self.agrupamiento:
            return 'agrupamiento'
        elif self.regla:
            return 'regla'
        elif self.nuevo_cargo:
            return 'nuevo_cargo'

    def _get_hiscars_filter(self):
        if self.cargo:
            q = Q(cargo=self.cargo.codigo[4:])
        elif self.agrupamiento:
            q = Q()
            for cargo in self.agrupamiento.cargo.all():
                q.add(Q(cargo=cargo.codigo[4:]), Q.OR)
        elif self.regla:
            q = Q(cargo__startswith=self.regla[4:].replace('%', ''))  # FIXME sacar reparticion de regla
        return q

    def add_orden(self):
        try:
            aumentos_movimiento = Aumento.objects.filter(movimiento=self.movimiento.id).order_by('-orden')
            if aumentos_movimiento:
                last_orden = aumentos_movimiento.values_list('orden', flat=True)[0]
            else:
                last_orden = 0
        except:
            last_orden = None

        if not last_orden or last_orden == 0:
            self.orden = 1
        else:
            self.orden = last_orden + 1

    def eliminar_ordenado(self):
        aumentos_movimiento = Aumento.objects.filter(movimiento=self.movimiento.id).order_by('orden')
        lista_ordenes = list(aumentos_movimiento.values_list('orden', flat=True))

        # Si no es el ultimo
        if not lista_ordenes.index(self.orden) + 1 == len(lista_ordenes):

            # Si no es el primero
            if not lista_ordenes.index(self.orden) == 0:
                # corto la lista desde el orden dado hasta el final.
                lista_ordenes = lista_ordenes[lista_ordenes.index(self.orden):]

            # recorro los aumentos del movimiento y les bajo el orden en uno.
            for aumento in aumentos_movimiento:
                if aumento.orden in lista_ordenes:
                    aumento.orden = aumento.orden - 1
                    aumento.save()

        self.delete()

    def getHiscarRegla(self):
        return Cargo.objects.filter(codigo__startswith=self.regla.replace('%', ''))

    def getHiscar(self, periodo, hiscar=[]):
        if self.cargo:
            hiscar = hiscar + [self.cargo.getHiscar(periodo, self)]
        else:
            if self.agrupamiento:
                hiscar = hiscar + self.agrupamiento.getHiscars(periodo, self)
            else:
                if self.regla:
                    for cargo in self.getHiscarRegla():
                        hiscar = hiscar + [cargo.getHiscar(periodo, self)]
        return hiscar

    # getHiscar llama correspondientemente al getHiscar de agrup o cargo
    def getHiscars(movimiento_id, periodo):
        hiscar = []
        aumentos = Aumento.objects.filter(movimiento=movimiento_id)
        for aumento in aumentos:
            hiscar = aumento.getHiscar(periodo, hiscar)
        return hiscar
