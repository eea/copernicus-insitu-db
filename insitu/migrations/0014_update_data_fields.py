# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0013_auto_20171101_1401"),
    ]

    operations = [
        migrations.AlterField(
            model_name="data",
            name="essential_variables",
            field=models.ManyToManyField(blank=True, to="picklists.EssentialVariable"),
        ),
        migrations.AlterField(
            model_name="data",
            name="inspire_themes",
            field=models.ManyToManyField(blank=True, to="picklists.InspireTheme"),
        ),
        migrations.AlterField(
            model_name="data",
            name="end_time_coverage",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="data",
            name="start_time_coverage",
            field=models.DateField(blank=True, null=True),
        ),
    ]
