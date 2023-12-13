from django.db import models


from main.models import CustomModel
from hiscar.models import Reparticion


class CuadriculaMovimiento(CustomModel):
    codigo        = models.CharField(max_length=120)
    periodo_dd    = models.DateField(
                    auto_now=False,
                    auto_now_add=False,
                    default=None,
                    null=True,
                    db_index=True)
    periodo_ht    = models.DateField(
                    auto_now=False,
                    auto_now_add=False,
                    default=None,
                    null=True,
                    db_index=True)
    nombre        = models.CharField(max_length=120)
    observaciones = models.CharField(max_length=500, null=True, blank=True)
    proyecto      = models.ForeignKey(
                    'aumentos.Proyecto',
                    on_delete=models.DO_NOTHING,
                    blank=True, null=True,
                    default=None)
    reparticion   = models.ForeignKey(
                    Reparticion,
                    on_delete=models.CASCADE,
                    blank=True, null=True)

    class Meta:
        db_table = 'cuadriculas'
        managed = True

    def __str__(self):
        return f'{self.codigo} {self.nombre}'

    def movimiento_bash(self):
        return f"""
            HISCAR=$intermedios/HISC.{self.codigo}
            export HISCAR
            echo HISCAR=$HISCAR >> $archivoDeLog


            echo "`date` - Comienza ejecucion de: {self.nombre}{self.codigo}"
            echo "`date` - Comienza ejecucion de: {self.nombre}{self.codigo}" >> $archivoDeLog
            cobrun $src/{self.nombre}{self.codigo} << EOJ >> $archivoDeLog 2> $log/ERROR.PGM
            $FHIS
            EOJ
            Resultado=$?
            if test $Resultado -eq 254
            then echo "`date` - Fin ejecucion de: {self.nombre}{self.codigo}, error 254 (cancelado)" >> $archivoDeLog
            elif test $Resultado -eq 255
            then echo "`date` - Fin ejecucion de: {self.nombre}{self.codigo}, error 255 (error de programa)" >> $archivoDeLog
            banner 'ERROR PGM.'
            exit
            else
            echo "`date` - Fin ejecucion de: {self.nombre}{self.codigo}, finalizacion OK" >> $archivoDeLog
            fi

        """.replace('            ', '')


class Comment(CustomModel):
    text = models.TextField(blank=True, null=True, default='')
    cuadricula_movimiento = models.ForeignKey(CuadriculaMovimiento, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'comments'
        managed = True

    def __str__(self):
        if self.modifier:
            return f'Comentario de {self.modifier}'
        else:
            return f'Comentario de {self.creator}'
