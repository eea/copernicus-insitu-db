# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-20 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("picklists", "0002_requirementgroup"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResponsibleType",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
