# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-02-05 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0011_auto_20180131_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataformat',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='datapolicy',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='timeliness',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='updatefrequency',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
