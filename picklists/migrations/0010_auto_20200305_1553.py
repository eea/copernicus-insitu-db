# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-05 15:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0009_rename_coverage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductStatus',
            new_name='Status',
        ),
    ]