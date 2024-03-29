# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-20 11:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("picklists", "0002_requirementgroup"),
        ("insitu", "0004_auto_20170720_1126"),
    ]

    operations = [
        migrations.AddField(
            model_name="data",
            name="dissemination",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.Dissemination",
            ),
            preserve_default=False,
        ),
    ]
