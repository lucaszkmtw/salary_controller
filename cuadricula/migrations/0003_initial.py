# Generated by Django 4.0 on 2021-12-26 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hiscar', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('cuadricula', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuadriculamovimiento',
            name='reparticion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.reparticion'),
        ),
        migrations.AddField(
            model_name='comment',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creator', to='auth.user'),
        ),
        migrations.AddField(
            model_name='comment',
            name='cuadricula_movimiento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cuadricula.cuadriculamovimiento'),
        ),
        migrations.AddField(
            model_name='comment',
            name='eliminator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_eliminator', to='auth.user'),
        ),
        migrations.AddField(
            model_name='comment',
            name='modifier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_modifier', to='auth.user'),
        ),
    ]