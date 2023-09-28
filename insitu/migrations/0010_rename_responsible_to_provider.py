# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-23 09:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("picklists", "0005_rename_responsible_to_provider"),
        ("insitu", "0009_rename_data_provider"),
    ]

    operations = [
        migrations.CreateModel(
            name="CopernicusProvider",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="provider",
                        to="insitu.CopernicusService",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_resp",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CountryProvider",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="provider",
                        to="picklists.Country",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="country_resp",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.RenameModel(
            old_name="DataResponsible",
            new_name="DataProvider",
        ),
        migrations.RenameModel(
            old_name="DataResponsibleDetails",
            new_name="DataProviderDetails",
        ),
        migrations.RenameModel(
            old_name="DataResponsibleRelation",
            new_name="DataProviderRelation",
        ),
        migrations.RemoveField(
            model_name="copernicusresponsible",
            name="service",
        ),
        migrations.RemoveField(
            model_name="copernicusresponsible",
            name="user",
        ),
        migrations.RemoveField(
            model_name="countryresponsible",
            name="country",
        ),
        migrations.RemoveField(
            model_name="countryresponsible",
            name="user",
        ),
        migrations.AlterModelOptions(
            name="dataproviderdetails",
            options={"verbose_name_plural": "data provider details"},
        ),
        migrations.RenameField(
            model_name="dataproviderdetails",
            old_name="data_responsible",
            new_name="data_provider",
        ),
        migrations.RenameField(
            model_name="dataproviderdetails",
            old_name="responsible_type",
            new_name="provider_type",
        ),
        migrations.RenameField(
            model_name="dataproviderrelation",
            old_name="responsible",
            new_name="provider",
        ),
        migrations.RemoveField(
            model_name="data",
            name="responsibles",
        ),
        migrations.RemoveField(
            model_name="dataprovideruser",
            name="responsible",
        ),
        migrations.AddField(
            model_name="data",
            name="providers",
            field=models.ManyToManyField(
                through="insitu.DataProviderRelation", to="insitu.DataProvider"
            ),
        ),
        migrations.AddField(
            model_name="dataprovideruser",
            name="provider",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="provider",
                to="insitu.DataProvider",
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="CopernicusResponsible",
        ),
        migrations.DeleteModel(
            name="CountryResponsible",
        ),
    ]
