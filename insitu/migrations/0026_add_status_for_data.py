# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-26 11:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0009_rename_coverage'),
        ('insitu', '0025_add_geographical_coverage'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='+', to='picklists.ProductStatus'),
        ),
    ]
