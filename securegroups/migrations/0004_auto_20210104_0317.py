# Generated by Django 3.1.1 on 2021-01-04 03:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('securegroups', '0003_smartfilter_grace_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graceperiodrecord',
            name='grace_filter',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='securegroups.smartfilter'),
        ),
    ]
