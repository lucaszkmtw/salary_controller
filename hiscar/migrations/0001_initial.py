# Generated by Django 4.0 on 2021-12-26 14:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_results', '0010_remove_duplicate_indices'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('aumentos', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agrupamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('nombre', models.CharField(db_index=True, max_length=60)),
            ],
            options={
                'db_table': 'agrupamientos',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ArchivoHiscar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileHash', models.CharField(default='', max_length=33, unique=True)),
                ('archivo', models.FilePathField(null=True, path='hiscar/')),
                ('peso', models.BigIntegerField()),
                ('cant_lineas', models.IntegerField(blank=True, default=None, null=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('split', models.BooleanField(default=False)),
                ('parsed', models.BooleanField(default=False, null=True)),
                ('priority', models.PositiveIntegerField(default=0)),
                ('autor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario_cargador', to='auth.user')),
            ],
            options={
                'db_table': 'archivos_hiscar',
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='Reparticion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('codigo', models.CharField(db_index=True, max_length=10)),
                ('nombre', models.CharField(db_index=True, max_length=500)),
                ('has_modulo', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
            ],
            options={
                'db_table': 'reparticiones',
            },
        ),
        migrations.CreateModel(
            name='TipoModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('codigo', models.CharField(max_length=3)),
                ('nombre', models.CharField(max_length=120)),
                ('is_default', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
                ('reparticion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.reparticion')),
            ],
            options={
                'db_table': 'tipo_modulo',
            },
        ),
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=18)),
                ('periodo', models.CharField(default='202112', max_length=6)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
                ('reparticion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.reparticion')),
                ('tipo', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='hiscar.tipomodulo')),
            ],
            options={
                'db_table': 'modulos',
            },
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('codigo', models.CharField(db_index=True, max_length=15)),
                ('cargo', models.CharField(db_index=True, max_length=200)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
                ('reparticion', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Cargo_reparticion', to='hiscar.reparticion')),
            ],
            options={
                'db_table': 'cargos',
            },
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('periodo', models.CharField(default='202112', max_length=6)),
                ('cargo', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='hiscar.cargo')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
                ('reparticion', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='hiscar.reparticion')),
                ('tipo', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='hiscar.tipomodulo')),
            ],
            options={
                'db_table': 'asignaciones',
            },
        ),
        migrations.CreateModel(
            name='ArchivoTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hiscar.archivohiscar')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='django_celery_results.taskresult')),
            ],
        ),
        migrations.AddField(
            model_name='archivohiscar',
            name='reparticion',
            field=models.ManyToManyField(related_name='reparticiones', to='hiscar.Reparticion'),
        ),
        migrations.AddField(
            model_name='archivohiscar',
            name='task',
            field=models.ManyToManyField(related_name='task_result', through='hiscar.ArchivoTask', to='django_celery_results.TaskResult'),
        ),
        migrations.CreateModel(
            name='AgrupamientoCargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('agrupamiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agrupamiento_int', to='hiscar.agrupamiento')),
                ('cargo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cargo_int', to='hiscar.cargo')),
            ],
            options={
                'db_table': 'agrupamiento_cargo',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='agrupamiento',
            name='cargo',
            field=models.ManyToManyField(through='hiscar.AgrupamientoCargo', to='hiscar.Cargo'),
        ),
        migrations.AddField(
            model_name='agrupamiento',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user'),
        ),
        migrations.AddField(
            model_name='agrupamiento',
            name='eliminator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user'),
        ),
        migrations.AddField(
            model_name='agrupamiento',
            name='modifier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user'),
        ),
        migrations.AddField(
            model_name='agrupamiento',
            name='reparticion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.reparticion'),
        ),
        migrations.CreateModel(
            name='Hiscar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('periodo', models.DateField(db_index=True, default=None, null=True)),
                ('cargo', models.CharField(db_index=True, max_length=11)),
                ('reparticion', models.CharField(blank=True, db_index=True, default=None, max_length=4, null=True)),
                ('basico', models.DecimalField(decimal_places=2, max_digits=18)),
                ('suplemento1', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('suplemento2', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('antiguedad', models.TextField(default=None, null=True)),
                ('sumafija1', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('sumafija2', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('sumafija3', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('archivo', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.archivohiscar')),
                ('aumento', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hiscar_from_aumento', to='aumentos.aumento')),
                ('cargo_obj', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cargo_objecto', to='hiscar.cargo')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user')),
                ('eliminator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user')),
                ('modifier', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user')),
                ('reparticion_obj', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Reparticion_objecto', to='hiscar.reparticion')),
            ],
            options={
                'db_table': 'hiscars',
                'unique_together': {('periodo', 'cargo', 'reparticion', 'archivo')},
            },
        ),
    ]
