# Generated by Django 3.2.20 on 2023-11-28 18:18

from django.db import migrations, models
import django.db.models.deletion


def set_data_provider_link(apps, schema_editor):
    UseCase = apps.get_model("use_cases", "UseCase")
    DataProvider = apps.get_model("insitu", "DataProvider")
    for use_case in UseCase.objects.all():
        data_provider = DataProvider.objects.filter(name=use_case.data_provider).first()
        if data_provider:
            use_case.data_provider_link = data_provider
            use_case.save()


def unset_data_provider_link(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('insitu', '0048_merge_20230831_0717'),
        ('use_cases', '0009_auto_20230915_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='link',
            field=models.URLField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='usecase',
            name='components',
            field=models.ManyToManyField(to='insitu.Component'),
        ),
        migrations.AddField(
            model_name='usecase',
            name='data_provider_link',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='insitu.dataprovider'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='source',
            field=models.TextField(max_length=256),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='copernicus_services',
            field=models.ManyToManyField(to='insitu.CopernicusService'),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='data_provider',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='locality',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='region',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.RunPython(set_data_provider_link, unset_data_provider_link),
    ]
