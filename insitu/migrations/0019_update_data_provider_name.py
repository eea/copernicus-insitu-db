# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-12 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0018_remove_mandatory_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataprovider",
            name="name",
            field=models.CharField(max_length=255),
        ),
    ]
