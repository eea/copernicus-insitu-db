# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-01 09:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0010_auto_20200305_1553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['sort_order'], 'verbose_name_plural': 'status'},
        ),
        migrations.AlterModelOptions(
            name='updatefrequency',
            options={'ordering': ['sort_order'], 'verbose_name_plural': 'update frequency'},
        ),
    ]