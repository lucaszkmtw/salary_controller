import os
import json
import datetime
import decimal

from django.db import models
from django.utils.timezone import now
from django.core.cache import cache

from django.contrib.auth.models import User
from django_celery_results.models import TaskResult

from main.functions import get_periodo_actual
from main.models import CustomModel

from hiscar.tasks import slice_and_parse_file
from django.conf import settings


class Reparticion(CustomModel):
    codigo = models.CharField(max_length=10, db_index=True)
    nombre = models.CharField(max_length=500, db_index=True)
    has_modulo = models.BooleanField(default=False)

    class Meta:
        db_table = 'reparticiones'

    def __str__(self):
        return self.codigo + ' - ' + self.nombre


class ArchivoHiscar(models.Model):
    """
    ArchivoHiscar : modelo que contiene los datos del archivo, del
    cual se importo el "Exporthiscar".

    Args:
        fileHash (char) : Hash para identificar archivo y no repetirlos.
        autor (user) : Usuario que subió el archivo.
        archivo : Nombre del archivo.
        peso (integer) : peso del archivo.
        fecha (date) : fecha de subida del archivo.
    """

    fileHash = models.CharField(
        max_length=33,
        unique=True,
        null=False,
        default='')
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="usuario_cargador")
    archivo = models.FilePathField(path='hiscar/', allow_files=True, null=True)
    peso = models.BigIntegerField()
    cant_lineas = models.IntegerField(null=True, blank=True, default=None)
    fecha = models.DateTimeField(default=now)
    split = models.BooleanField(default=False)
    parsed = models.BooleanField(default=False, null=True)
    priority = models.PositiveIntegerField(default=0, blank=False, null=False)
    task = models.ManyToManyField(
        TaskResult,
        through="ArchivoTask",
        related_name="task_result")
    reparticion = models.ManyToManyField(
        Reparticion,
        related_name="reparticiones")

    class Meta:
        db_table = 'archivos_hiscar'
        ordering = ['priority']

    def __str__(self):
        """__str__ ArchivoHiscar to string.

        Returns:
            string : formato de impresion de ArchivoHiscar
        """
        if self.archivo:
            return str(self.archivo.split('/')[-1])
        else:
            return '-'

    def hash_file(self, block_size=65536):
        """
        hash_file : Hashea el archivo a partir del contenido para evitar que
            suban dos veces el mismo archivo.

        Args:
            file (archivo): Ruta del archivo.
            block_size (int, optional): Tamaño del bloque de hash. Defaults
                to 65536.

        Returns:
            string: código de hash correspondiente
        """
        import hashlib
        # Si ya había un archivo y ahora ya no esta en el almacenamiento
        if self.fileHash and not os.path.exists(str(self.archivo)):
            raise Exception(f'File {self.archivo} does not exist!')
        else:
            hasher = hashlib.md5()
            with open(os.path.join(settings.MEDIA_ROOT, self.archivo), mode='rb') as f:
                for chunk in iter(lambda: f.read(block_size), b''):
                    hasher.update(chunk)
                return hasher.hexdigest()

    def guardarArchivo(self, uploaded_file, user):
        """
        guardarArchivo:
            almacena el archivo en temporales, lo
        procesa y almacena los cargos parseados en la base
        de datos.

        Args:
            uploaded_file (archivo): Ruta del archivo
            user (user): user que subió el archivo
        """
        self.archivo = uploaded_file
        # hashArchivo = self.hash_file() # HOTFIX de tiempos
        hashArchivo = ''
        already_exists = ArchivoHiscar.objects.filter(
            fileHash=hashArchivo).exists()
        if not already_exists:
            self.fileHash = hashArchivo
            self.autor = user
            self.peso = os.path.getsize(self.archivo)
            self.fecha = now()
            self.save()
        else:
            raise Exception('El archivo ya existe')

    def split_process_hiscar_file(self, user_id):
        """Proceso que corta el archivo en pedazos y parcea cada uno por separado
           en un proceso paralelo.

        Args:
            user_id (User): Usuario que genera la tarea.
        """
        slice_and_parse_file\
            .delay(
                archivo_hiscar_id=self.id,
                user_id=user_id
            )
        return True


class ArchivoTask(models.Model):
    task = models.ForeignKey(TaskResult, on_delete=models.DO_NOTHING)
    archivo = models.ForeignKey(ArchivoHiscar, on_delete=models.CASCADE)


class Cargo(CustomModel):
    reparticion = models.ForeignKey(
        Reparticion,
        default=None,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="Cargo_reparticion")
    codigo = models.CharField(max_length=15, db_index=True)
    cargo = models.CharField(max_length=200, db_index=True)

    class Meta:
        db_table = 'cargos'

    def __str__(self):
        return self.codigo

    def natural_key(self):
        return (self.id, self.codigo, self.cargo)

    def get_valor_modulo(self, exporthiscar, periodo):
        basico = exporthiscar.values_list('basico', flat=True)[0]

        valor_modulo = Modulo.objects.filter(
            reparticion=46,
            # tipo=tipo,
            periodo=int(periodo) - 1,
            is_active=True).values_list('valor', flat=True)[0]
        return float(basico) / float(valor_modulo)

    def calcular_aumento(self, campo, tipo_calculo_id, valor):
        """
        calcular_aumento : Calcula el valor del aumento teniendo en cuenta el
            tipo de calculo (porcentual/sumafija).

        Args:
            campo (integer): representa el campo al que se va a aumentar, ej.
                Basico, Sumafij1..
            tipo_calculo_id (id): Representa el tipo de calculo que se va a
            ejecutar, ej. sumafija, porcentual..
            valor (float): valor correspondiente al aumento

        Returns:
            float: Nuevo valor del campo ya calculado
        """
        campo = float(campo)
        valor = float(valor)
        if tipo_calculo_id == 1:
            return "{0:.2f}".format(campo + ((campo * valor) / 100))
        elif tipo_calculo_id == 2:
            return "{0:.2f}".format(campo + valor)

    def getCargosByCache(reparticion_id):
        """getCargosByCache Devuelve los cargos cacheados en un rango de una
        hora.

        Args:
            reparticion_id (integer): ID correspondiente a la reparticion
            reparticion_id (integer): ID correspondiente a la reparticion

        Returns:
            Cargos: Cargos correspondientes a la reparticion y el usuario
        """
        hoy = now()
        mes_actual = str(hoy.month - 1).zfill(2)     # DESPUES BORRAR EL -1
        ano_actual = str(hoy.year)
        key_cache = mes_actual + ano_actual + str(reparticion_id)
        if not cache.get(key_cache):
            reparticion = Reparticion.objects.get(id=reparticion_id).codigo
            if((reparticion.find("-1")) != -1):
                reparticion = reparticion[:(reparticion.find("-1"))]
            cargos = Cargo.objects.filter(
                is_active=True, reparticion_id=reparticion_id).values('id', 'codigo', 'cargo')
            cache.set(key_cache, cargos, 3600)
            return cargos
        else:
            return cache.get(key_cache)

    def getHiscar(self, periodo, aumento):
        """
        getHiscar : devuelve el objeto ExportHiscar calculado correspondiente
            al aumento.

        Args:
            periodo (integer): Periodo correspondiente al cargo.
            aumento (integer): ID correspondiente al Aumento.

        Returns:
            Hiscar : devuelve Hiscar con cargado con los valores del aumento
                aplicado.
        """
        hiscar_id = Hiscar.objects.filter(
            cargo=self.codigo).values_list(
                'id', flat=True).order_by('-periodo')[1]

        hiscar = Hiscar.objects.get(id=hiscar_id)

        # Se intercambia el id de exporthiscar por el de su correspondiente aumento.
        hiscar.id = aumento.id
        if aumento.tipo_aumento.id == 1:
            hiscar.basico = self.calcular_aumento(
                hiscar.basico, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 2:
            hiscar.suplemento1 = self.calcular_aumento(
                hiscar.suplemento1, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 3:
            hiscar.suplemento2 = self.calcular_aumento(
                hiscar.suplemento2, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 4:
            hiscar.antiguedad = self.calcular_aumento(
                hiscar.antiguedad, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 5:
            hiscar.sumafija1 = self.calcular_aumento(
                hiscar.sumafija1, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 6:
            hiscar.sumafija2 = self.calcular_aumento(
                hiscar.sumafija2, aumento.tipo_calculo.id, aumento.valor)
        if aumento.tipo_aumento.id == 7:
            hiscar.sumafija3 = self.calcular_aumento(
                hiscar.sumafija3, aumento.tipo_calculo.id, aumento.valor)

        return hiscar


class Agrupamiento(CustomModel):
    nombre = models.CharField(max_length=60, db_index=True)
    reparticion = models.ForeignKey(Reparticion, on_delete=models.CASCADE, blank=True, null=True)
    cargo = models.ManyToManyField(Cargo, through='AgrupamientoCargo')

    class Meta:
        managed = True
        db_table = 'agrupamientos'

    def __str__(self):
        return self.nombre

    def natural_key(self):
        return (self.id, self.nombre)

    def update(vector_agrupamientos, agrupamiento_id, reparticion_id, nombre, movimiento_id, user):
        from aumentos.models import Aumento
        agrupamiento_old = Agrupamiento.objects.get(id=agrupamiento_id)
        agrupamiento_old.is_active = False
        agrupamiento_old.modified = now()
        agrupamiento_old.save()

        agrupamiento_new = Agrupamiento(
            nombre=nombre,
            reparticion=Reparticion.objects.get(id=reparticion_id),
            creator=user
        )
        agrupamiento_new.save()

        aumentos = Aumento.objects.filter(
            movimiento=movimiento_id,
            agrupamiento=agrupamiento_old.id)

        for aumento in aumentos:
            aumento.agrupamiento = agrupamiento_new
            aumento.save()

        AgrupamientoCargo.update(vector_agrupamientos, agrupamiento_old, agrupamiento_new, nombre, user)

        return agrupamiento_new

    def getCargos(self):
        agrupamientos_cargos = AgrupamientoCargo.objects.filter(agrupamiento=self.id)
        id_cargos = []
        for agrup_cargo in agrupamientos_cargos:
            id_cargos.append(agrup_cargo.cargo.id)
        cargos = Cargo.objects.filter(id__in=id_cargos)
        return cargos

    def getCargosNombres(self):
        cargos = []
        agrupamiento_cargos = AgrupamientoCargo.objects.filter(agrupamiento=self.id)
        for agrup_cargo in agrupamiento_cargos:
            cargos.append(agrup_cargo.getCargo())
        return cargos

    def eliminarObjectoSeleccionado(id):
        try:
            Agrupamiento.objects.filter(id=id).delete()
        except Agrupamiento.DoesNotExist:
            return False
        return True

    # getHiscar llama al getHiscar de Agrupamiento_cargo
    def getHiscars(self, periodo, aumento):
        lista = []
        agrupamiento = AgrupamientoCargo.objects.filter(agrupamiento=self.id)
        for agrup_cargo in agrupamiento:
            lista.append(agrup_cargo.getHiscar(periodo, aumento))
        return lista


class AgrupamientoCargo(models.Model):
    agrupamiento = models.ForeignKey(Agrupamiento, related_name='agrupamiento_int', on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, related_name='cargo_int', on_delete=models.CASCADE)

    created = models.DateTimeField(default=now)
    modified = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'agrupamiento_cargo'

    def __str__(self):
        return str(self.agrupamiento) + str(self.cargo)

    def getCargo(self):
        return str(Hiscar.objects.filter(cargo=self.cargo.codigo))

    def getAgrupamiento(self):
        return AgrupamientoCargo.agrupamiento

    def new(vector_agrupamientos: list, nombre_agrupamiento, reparticion_id, user):
        agrupamiento = Agrupamiento(
            nombre=nombre_agrupamiento,
            reparticion=Reparticion.objects.get(id=reparticion_id),
            creator=user)
        agrupamiento.save()

        for cargo in vector_agrupamientos:
            agrupCargo = AgrupamientoCargo()
            agrupCargo.agrupamiento = agrupamiento
            agrupCargo.cargo = Cargo.objects.get(id=int(cargo))
            agrupCargo.save()
        return agrupamiento

    def update(vector_agrupamientos: list, agrupamiento_old, agrupamiento_new, nombre, user):
        """
        Updatea todos los AgrupCargos con ID = Agrupamiento
        """
        lista_cargos = []
        for agrup_cargo in AgrupamientoCargo.objects.filter(agrupamiento=agrupamiento_old.id):
            # Cambio el id del agrupamiento de AgrupCargo por el nuevo
            agrup_cargo.agrupamiento = agrupamiento_new
            agrup_cargo.save()
            # Te traes todos los agrupcargos del Agrupamiento
            # Si el id NO esta en la lista de cargos lo elimino sino lo agrego al vector lista_cargos
            if str(agrup_cargo.cargo.id) not in vector_agrupamientos:
                agrup_cargo.delete()
            else:
                lista_cargos.append(str(agrup_cargo.cargo.id))

        # Si es un AgrupCargo nuevo lo creo y lo guardo
        for agrup_cargo in vector_agrupamientos:
            if str(agrup_cargo) not in lista_cargos:
                agrupCargo = AgrupamientoCargo()
                agrupCargo.agrupamiento = agrupamiento_new
                agrupCargo.cargo = Cargo.objects.get(id=int(agrup_cargo))
                agrupCargo.save()

    # getHiscar llama al getHiscar de Cargo
    def getHiscar(self, periodo, aumento):
        return self.cargo.getHiscar(periodo, aumento)


class Hiscar(CustomModel):
    periodo = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=None,
        null=True,
        db_index=True)
    cargo = models.CharField(max_length=11, db_index=True)
    reparticion = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        db_index=True)
    basico = models.DecimalField(
        max_digits=18,
        decimal_places=2)
    suplemento1 = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True)
    suplemento2 = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True)
    antiguedad = models.TextField(
        null=True,
        default=None)
    sumafija1 = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True)
    sumafija2 = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True)
    sumafija3 = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True)
    cargo_obj = models.ForeignKey(
        Cargo,
        default=None,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="cargo_objecto")
    reparticion_obj = models.ForeignKey(
        Reparticion,
        default=None,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="Reparticion_objecto")
    archivo = models.ForeignKey(
        ArchivoHiscar,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None)
    aumento = models.ForeignKey(
        'aumentos.Aumento',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        related_name="hiscar_from_aumento")

    HLS = {
        'periodo': {'dd': 1, 'ht': 8},
        'reparticion': {'dd': 10, 'ht': 14},
        'cargo': {'dd': 14, 'ht': 25}}

    HLS2 = {
        'basico': {'dd': 26, 'ht': 38},
        'suplemento1': {'dd': 39, 'ht': 51},
        'suplemento2': {'dd': 52, 'ht': 64},
        'antiguedad': {'dd': 65, 'ht': 77},
        'sumafija1': {'dd': 78, 'ht': 90},
        'sumafija2': {'dd': 91, 'ht': 104},
        'sumafija3': {'dd': 105, 'ht': 118}}

    HLSV = {
        'periodo': {'dd': 0, 'ht': 6},
        'reparticion': {'dd': 6, 'ht': 10},
        'cargo': {'dd': 10, 'ht': 21}}

    HLSV2 = {
        'basico': {'dd': 21, 'ht': 32},
        'suplemento1': {'dd': 32, 'ht': 43},
        'suplemento2': {'dd': 43, 'ht': 54},
        'antiguedad': {'dd': 54, 'ht': 505},
        'sumafija1': {'dd': 505, 'ht': 516},
        'sumafija2': {'dd': 516, 'ht': 527},
        'sumafija3': {'dd': 527, 'ht': 536}}

    class Meta:
        db_table = 'hiscars'
        unique_together = [['periodo', 'cargo', 'reparticion', 'archivo']]

    def __str__(self):
        """__str__ Hiscar to string.

        Returns:
            string : formato de impresion de Hiscar.
        """
        return str(self.periodo) + ' - ' + self.cargo

    def serialize(self):
        return json.dumps({
            'periodo': self.periodo,
            'cargo': self.cargo,
            'basico': float(0 if not self.basico else self.basico),
            'antiguedad': float(0 if not self.antiguedad else self.antiguedad),
            'suplemento1': float(0 if not self.suplemento1 else self.suplemento1),
            'suplemento2': float(0 if not self.suplemento2 else self.suplemento2),
            'sumafija1': float(0 if not self.sumafija1 else self.sumafija1),
            'sumafija2': float(0 if not self.sumafija2 else self.sumafija2),
            'sumafija3': float(0 if not self.sumafija3 else self.sumafija3)
        })

    def generate_line(self, periodo=None):
        line = [' '] * 118
        HLS = {**self.HLS, **self.HLS2}
        for key in HLS.keys():
            if isinstance(getattr(self, key), (float, decimal.Decimal)):
                attr_str = "{:.2f}".format(getattr(self, key)).replace('.', ',')
            else:
                attr_str = getattr(self, key)
            if periodo and key == 'periodo':
                attr_str = str(periodo)[:7]
            if key != 'antiguedad':
                for i in range(len(attr_str)):
                    line[
                        HLS[key]['dd'] + int(
                            HLS[key]['ht'] - HLS[key]['dd'] - len(attr_str)
                        ) + i
                    ] = attr_str[i]
        return ''.join(line)

    def generate_file(movimiento_id):
        from aumentos.models import Movimiento, Aumento
        txt = ''
        movimiento = Movimiento.objects.get(id=movimiento_id)
        aumentos = Aumento.objects.filter(movimiento_id=movimiento_id)
        hiscars = Hiscar.objects.filter(aumento_id__in=[a.id for a in aumentos]).all()
        for p in range(movimiento.periodo_dd, movimiento.periodo_ht + 1, 1):
            for h in hiscars:
                txt += h.generate_line(p) + '\n'
        return txt

    def parse_line(self, linea):
        """parse_line parsea una linea y la almacena en formato de Hiscar.

        Args:
            linea (integer): Linea extraida del archivo de texto plano, salida de cobol.

        Returns:
            Hiscar : objeto de Hiscar.
        """
        #  Periodo - Reparticion - Cargo
        for key in self.HLS.keys():
            attr = linea[
                self.HLS[key]['dd']:
                self.HLS[key]['ht']
            ]
            attr = datetime.datetime.strptime(attr, "%Y-%m").date() if key == 'periodo' else attr

            setattr(
                self,
                key,
                attr
            )

        for key in self.HLS2.keys():
            line = linea[
                self.HLS2[key]['dd']:
                self.HLS2[key]['ht']
            ]\
                .strip()\
                .replace('.', '')\
                .replace(',', '.')
            setattr(
                self,
                key,
                float(line) if not line == '' else 0
            )

    def parse_file(nombreArchivo, arch):
        """parse_file Recorre todo el archivo secuencialmente haciendo
        llamadas en caso que la linea contenga un formato de Hiscar parseable
        lo parsea y almacena Hasta EOF.

        Args:
            nombreArchivo (string): Nombre del archivo que se subió.
            arch (ArchivoHiscar): ArchivoHiscar objeto que hace referencia al archivo de donde salio.
        """
        archivo = open('media/' + nombreArchivo, 'r')
        i = 1
        for linea in archivo.readlines():
            if (linea[:2] == ' 2'):
                hiscar = Hiscar.parse_line(linea)
                hiscar.archivo = arch
                hiscar.save()
            i += 1

    def parse_line_vec_antiguedad(self, linea):
        def parse_float(string):
            return float(f"{string[:-2]}.{string[-2:]}")

        #  Periodo - Reparticion - Cargo
        for key, pos in self.HLSV.items():
            attr = linea[pos['dd']:pos['ht']]
            attr = datetime.datetime.strptime(attr, "%Y%m").date() if key == 'periodo' else attr

            setattr(
                self,
                key,
                attr
            )

        for key, pos in self.HLSV2.items():
            if key == 'antiguedad':
                vec = []
                start = pos['dd']
                for i in range(0, 41):
                    vec.append(parse_float(linea[start + i * 11: start + i * 11 + 11]))
                val = json.dumps(vec)
            else:
                val = parse_float(linea[pos['dd']:pos['ht']])

            setattr(self, key, val)

    def generate_line_vec_antiguedad(self, periodo=None):
        line = [' '] * 536
        for key in self.HLSV:
            if periodo and key == 'periodo':
                attr_str = periodo.strftime('%Y%m')
            else:
                attr_str = str(getattr(self, key))

            for i in range(len(attr_str)):
                line[
                    self.HLSV[key]['dd'] + int(
                        self.HLSV[key]['ht'] - self.HLSV[key]['dd'] - len(attr_str)
                    ) + i
                ] = attr_str[i]

        for key in self.HLSV2:
            if key == 'antiguedad':
                attr_str = ''\
                    .join(format(e, ".2f")
                        .replace('.', '')
                        .replace(',', '')
                        .zfill(11) for e in json.loads(getattr(self, key)))
            else:
                attr_str = format(getattr(self, key), ".2f")\
                    .replace('.', '')\
                    .replace(',', '')\
                    .zfill(11)

            for i in range(len(attr_str)):
                line[
                    self.HLSV2[key]['dd'] + int(
                        self.HLSV2[key]['ht'] - self.HLSV2[key]['dd'] - len(attr_str)
                    ) + i
                ] = attr_str[i]

        return ''.join(line)

    def getHiscars(archivo_id):
        if archivo_id is not None:
            return Hiscar.objects.filter(archivo=archivo_id)

    def get_last_hiscar_by_codigo(self, cargo_codigo):
        return Hiscar.objects.raw(
            """SELECT TOP(1) * FROM hiscars
             WHERE cargo = %s
             ORDER BY periodo DESC """, [cargo_codigo]
        )


class TipoModulo(CustomModel):
    """
    TipoModulo : corresponde a los varios tipos modulos que puede tener una
    reparticion.
    """
    codigo = models.CharField(max_length=3, blank=False)
    nombre = models.CharField(max_length=120, blank=False)
    is_default = models.BooleanField(default=False)
    reparticion = models.ForeignKey(
        Reparticion,
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    class Meta:
        db_table = 'tipo_modulo'

    def __str__(self):
        return f"[{self.codigo}] - {self.reparticion.codigo} [{self.nombre}] {self.is_default}"


class Modulo(CustomModel):
    """
    Modulo : valores de los modulos correspondientes a un periodo y
        reparticion y a los cargos que la contienen.
    """
    reparticion = models.ForeignKey(
        Reparticion,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    periodo = models.CharField(max_length=6, default=get_periodo_actual())
    tipo = models.ForeignKey(
        TipoModulo,
        default=None,
        on_delete=models.CASCADE)

    class Meta:

        db_table = 'modulos'

    def __str__(self):
        return f"Modulo de {self.reparticion__codigo} - {str(self.periodo)[:4]} - {str(self.periodo)[4:6]}"

    def deactivate_module(self, reparticion_id, periodo, *args, **kwargs):
        """deactivate_module Desactivar modulo desactiva el o los modulos del
        periodo y municipio dados.

        Args:
            reparticion_id (integer): ID de la reparticion
            periodo (integer): periodo.
        """
        Modulo.objects.filter(
            reparticion_id=reparticion_id, periodo=periodo, is_active=True).update(is_active=0)

    def save(self, *args, **kwargs):
        """save redefine el save de modulo y desactiva el modulo anterior."""
        self.deactivate_module(self.reparticion_id, self.periodo)
        super(Modulo, self).save(*args, **kwargs)


class Asignacion(CustomModel):
    """
    Asignacion : Objeto que conecta a los cargos con su valor en modulos.
    """
    periodo = models.CharField(max_length=6, default=get_periodo_actual())
    reparticion = models.ForeignKey(
        Reparticion,
        default=None,
        on_delete=models.CASCADE)
    tipo = models.ForeignKey(
        TipoModulo,
        default=None,
        on_delete=models.CASCADE)
    cargo = models.ForeignKey(
        Cargo,
        default=None,
        on_delete=models.CASCADE)

    class Meta:
        db_table = 'asignaciones'

    def __str__(self):
        return self.cargo.codigo + ' - ' + self.tipo.nombre
