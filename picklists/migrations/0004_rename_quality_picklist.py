# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-19 14:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("picklists", "0003_responsibletype"),
        ("insitu", "0008_set_optional_fields"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Quality",
            new_name="QualityControlProcedure",
        ),
        migrations.AlterModelOptions(
            name="qualitycontrolprocedure",
            options={
                "ordering": ["sort_order"],
                "verbose_name_plural": "quality_control_procedure",
            },
        ),
    ]
