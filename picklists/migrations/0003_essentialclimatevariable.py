# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-16 13:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0002_auto_20170612_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='EssentialClimateVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.IntegerField(choices=[(0, 'ATMOSPHERIC'), (1, 'OCEANIC'), (2, 'TERRESTRIAL')])),
                ('component', models.IntegerField(choices=[(0, 'SURFACE'), (1, 'UPPER-AIR'), (2, 'COMPOSITION'), (3, 'PHYSICS'), (4, 'BIOGEOCHEMISTRY'), (5, 'BIOLOGY/ECOSYSTEMS'), (6, 'HYDROLOGICAL'), (7, 'CRYOSPHERE'), (8, 'CRYOSPHERE/BIOSPHERE'), (9, 'BIOSPHERE'), (10, 'HUMAN DIMENSION')])),
                ('parameter', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
    ]