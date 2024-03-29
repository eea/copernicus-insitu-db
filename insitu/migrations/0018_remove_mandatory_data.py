# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-30 12:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0017_rename_coverage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="data",
            name="area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.Area",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="data_format",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.DataFormat",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="data_policy",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.DataPolicy",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="data_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.DataType",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="dissemination",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.Dissemination",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="essential_variables",
            field=models.ManyToManyField(
                blank=True, null=True, to="picklists.EssentialVariable"
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="inspire_themes",
            field=models.ManyToManyField(
                blank=True, null=True, to="picklists.InspireTheme"
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="quality_control_procedure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.QualityControlProcedure",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="timeliness",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.Timeliness",
            ),
        ),
        migrations.AlterField(
            model_name="data",
            name="update_frequency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="picklists.UpdateFrequency",
            ),
        ),
    ]
