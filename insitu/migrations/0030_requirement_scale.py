# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-09-30 14:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0029_add_feedback_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="requirement",
            name="scale",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="insitu.Metric",
            ),
            preserve_default=False,
        ),
    ]
