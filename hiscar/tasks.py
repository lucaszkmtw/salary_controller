import os
import resource
from django.test import override_settings
from django.conf import settings
from project.celery import app
from django_celery_results.models import TaskResult
from django.contrib.auth.models import User
from fsplit.filesplit import Filesplit
from main.models import BulkCreateManager
from django.db import IntegrityError
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist

@app.task(bind=True)
def slice_and_parse_file(self, archivo_hiscar_id, user_id):
    from hiscar.models import ArchivoHiscar

    context = {}
    files = []

    def proccess_file_in_task(file_path, size=0):
        files.append(file_path.split('/')[-1])
        process_one_hiscar_file_task\
            .delay(
                archivo_hiscar_id=archivo_hiscar_id,
                user_id=user_id,
                file_dir=file_path
            )

    self.update_state(state='STARTED')

    archivo_hiscar = ArchivoHiscar.objects.get(id=archivo_hiscar_id)
    task_result = TaskResult.objects.get(task_id=self.request.id)
    archivo_hiscar.task.add(task_result)
    archivo_hiscar.save()

    dir_name = archivo_hiscar.archivo.split('/')[-1].replace(" ", "_").replace(".", "_")
    bulk_folder = f"{settings.MEDIA_ROOT}/hiscar/{dir_name}_fd"

    if not archivo_hiscar.parsed:

        if not os.path.exists(bulk_folder):  # Si ya no existia la carpeta
            os.mkdir(bulk_folder)  # Crea la carpeta
            fs = Filesplit()
            fs.split(
                file=archivo_hiscar.archivo,
                split_size=50_000_000,  # 50_000 bytes, 93_110 lineas, 853_388 kb la task
                output_dir=bulk_folder,
                newline=True,
                callback=proccess_file_in_task
            )
        else:
            files = os.listdir(bulk_folder)
            for file in files:
                proccess_file_in_task(
                    os.path.join(
                        bulk_folder,
                        file
                    )
                )

    os.remove(
        os.path.join(
            bulk_folder,
            'fs_manifest.csv'
        )
    )
    return context


@app.task(bind=True)
def process_one_hiscar_file_task(self, archivo_hiscar_id, user_id, file_dir):
    from hiscar.models import ArchivoHiscar
    from hiscar.models import Hiscar

    context = {}
    file_error = []

    def save_hiscar(line, archivo_hiscar, user):
        hiscar = Hiscar()
        try:
            hiscar.parse_line_vec_antiguedad(line)

        except ValueError as value_error:
            file_error.append(
                {
                    "line": line,
                    "error": value_error
                }
            )

        except Exception as e:
            raise e

        else:
            hiscar.archivo = archivo_hiscar
            hiscar.creator = user

        return hiscar

    self.update_state(state='STARTED')

    user = User.objects.get(id=user_id)

    # Get ArchivoHiscar
    archivo_hiscar = ArchivoHiscar.objects.get(id=archivo_hiscar_id)
    archivo_hiscar.task.add(TaskResult.objects.get(task_id=self.request.id))
    archivo_hiscar.save()

    hiscar_bulk = BulkCreateManager(chunk_size=10_000)

    self.update_state(state='PARSING FILES')
    try:
        with open(file_dir, 'r') as f:
            while line := f.readline():
                if line != '':
                    hiscar = save_hiscar(
                        line,
                        archivo_hiscar,
                        user
                    )
                    hiscar_bulk.add(hiscar)

    except FileNotFoundError as error:
        context['file'] = str(error)

    except IntegrityError as error:
        file_error.append(
            {
                "error": error
            }
        )

    except ArchivoHiscar.DoesNotExist:
        pass

    except Exception as error:
        raise error

    hiscar_bulk.done()
    os.remove(file_dir)

    if file_error:
        context['file_error'] = file_error

    context['memory'] = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} kb"
    return context


@app.task(bind=True)
def task_cargos_y_reps(self, user_id):
    from hiscar.models import Hiscar
    from hiscar.models import Reparticion
    from hiscar.models import Cargo
    self.update_state(state='STARTED')
    context = {}
    reparticiones = Hiscar.objects\
                          .values_list('reparticion', flat=True)\
                          .order_by('reparticion')\
                          .distinct()
                          
    cantidad_reparticiones = len(list(reparticiones))
    reparticiones = Hiscar.objects\
                          .values('reparticion')\
                          .order_by('reparticion')\
                          .distinct()\
                          .iterator()
    i = 0
    for reparticion_codigo in reparticiones:
        reparticion_codigo.get('reparticion')
        reparticion_codigo = reparticion_codigo.get('reparticion')
        i += 1
        self.update_state(
            state='PROGRESS',
            meta={
                'total': cantidad_reparticiones,
                'current': i
            }
        )

        try:
            reparticion = Reparticion.objects.get(nombre=reparticion_codigo)

        except Reparticion.DoesNotExist:

            reparticion = Reparticion(
                codigo=reparticion_codigo,
                nombre=reparticion_codigo,
                creator_id=1,
            )
            reparticion.save()

        hiscars = Hiscar.objects\
            .values('cargo')\
            .filter(reparticion=reparticion_codigo)\
            .order_by('cargo')\
            .distinct()

        cargos = Cargo.objects\
            .filter(reparticion=reparticion)

        cargos_faltantes = hiscars.difference(cargos)

        for cargo_codigo in cargos_faltantes:
            cargo_codigo=cargo_codigo.get('cargo') 

            cargo_nuevo = Cargo(
                codigo=cargo_codigo,
                cargo=cargo_codigo,
                reparticion=reparticion,
                creator_id=user_id,
            )
            cargo_nuevo.save()
        
            Hiscar.objects\
                    .filter(
                        cargo=cargo_codigo,
                        reparticion=reparticion_codigo)\
                    .update(
                        cargo_obj=cargo_nuevo,
                        reparticion_obj=reparticion)
    context['cantidad_reparticiones'] = cantidad_reparticiones
    return context


@app.task(bind=True)
def cargo_historico(self):
    from hiscar.models import Reparticion
    from hiscar.models import Cargo
    from hiscar.models import Hiscar

    reparticiones = Reparticion.objects.values_list('codigo', flat=True)

    for reparticion in reparticiones:

        fechas = Hiscar.objects.filter(reparticion=reparticion)\
            .values_list('periodo', flat=True)\
            .order_by('periodo')\
            .distinct()

        fecha_anterior = None
        for fecha in fechas:
            hiscar_anterior = Hiscar.objects\
                .filter(reparticion=reparticion, periodo=fecha_anterior)\
                .values_list('cargo', flat=True)\
                .order_by('cargo')

            hiscar_actual = Hiscar.objects\
                .filter(reparticion=reparticion, periodo=fecha)\
                .values_list('cargo', flat=True)\
                .order_by('cargo')

            fecha_anterior = fecha

            eliminados = hiscar_anterior.difference(hiscar_actual)
            creados = hiscar_actual.difference(hiscar_anterior)

            with override_settings(USE_TZ=False):
                for cargos in eliminados:
                    Cargo.objects\
                        .filter(cargo=cargos)\
                        .update(deleted=fecha)

                for cargos in creados:
                    Cargo.objects\
                        .filter(cargo=cargos)\
                        .update(created=fecha)

    lista_cargo = Cargo.objects.all()
    for cargo in lista_cargo:
        if cargo.deleted:
            deleted = cargo.deleted.strftime("%m/%d/%Y")
            created = cargo.created.strftime("%m/%d/%Y")
            if created < deleted:
                Cargo.objects.filter(cargo=cargo.codigo)\
                    .update(is_active=False)
            else:
                Cargo.objects.filter(cargo=cargo.codigo)\
                    .update(is_active=True)
