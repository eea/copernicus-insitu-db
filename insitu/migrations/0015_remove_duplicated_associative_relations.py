# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 10:49
from __future__ import unicode_literals

from django.db import migrations

# removed as those were used one time


def remove_product_requirement_duplicates(*args):
    pass


def remove_data_provider_duplicates(*args):
    pass


def remove_data_requirement_duplicates(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('insitu', '0014_update_data_fields'),
    ]

    operations = [
        migrations.RunPython(remove_product_requirement_duplicates),
        migrations.RunPython(remove_data_provider_duplicates),
        migrations.RunPython(remove_data_requirement_duplicates),
    ]
