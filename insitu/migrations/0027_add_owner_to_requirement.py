# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-26 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("insitu", "0026_add_status_for_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="requirement",
            name="owner",
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
