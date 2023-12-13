# Generated by Django 4.0 on 2021-12-26 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hiscar', '0001_initial'),
        ('aumentos', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aumento',
            name='agrupamiento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.agrupamiento'),
        ),
        migrations.AddField(
            model_name='aumento',
            name='cargo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hiscar.cargo'),
        ),
        migrations.AddField(
            model_name='aumento',
            name='movimiento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='aumentos.movimiento'),
        ),
    ]