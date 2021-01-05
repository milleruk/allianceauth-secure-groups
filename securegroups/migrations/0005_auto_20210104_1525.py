# Generated by Django 3.1.1 on 2021-01-04 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('securegroups', '0004_auto_20210104_0317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='altalliancefilter',
            options={'verbose_name': 'Smart Filter: Alt in Alliance',
                     'verbose_name_plural': 'Smart Filter: Alt in Alliance'},
        ),
        migrations.AlterModelOptions(
            name='altcorpfilter',
            options={'verbose_name': 'Smart Filter: Alt in Corporation',
                     'verbose_name_plural': 'Smart Filter: Alt in Corporation'},
        ),
        migrations.AlterModelOptions(
            name='smartfilter',
            options={'verbose_name': 'Smart Filter Catalog',
                     'verbose_name_plural': 'Smart Filter Catalog'},
        ),
        migrations.AlterField(
            model_name='smartfilter',
            name='content_type',
            field=models.ForeignKey(
                editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='smartfilter',
            name='object_id',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]