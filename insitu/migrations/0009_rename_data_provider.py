# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-20 13:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0008_set_optional_fields"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DataProvider",
            new_name="DataProviderUser",
        ),
    ]
