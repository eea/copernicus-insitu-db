# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-18 08:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0004_delete_targetdistance'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EssentialClimateVariable',
            new_name='EssentialVariable',
        ),
    ]