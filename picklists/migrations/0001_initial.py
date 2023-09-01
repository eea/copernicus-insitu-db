# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-19 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Barrier",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="ComplianceLevel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "code",
                    models.CharField(max_length=2, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name_plural": "countries",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Coverage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "coverage",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Criticality",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "criticality",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="DataFormat",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="DataType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="DefinitionLevel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Dissemination",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "dissemination",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="UpdateFrequency",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "update_frequency",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="InspireTheme",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("annex", models.CharField(blank=True, max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Policy",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "policy",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="ProductGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="ProductStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "product status",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Quality",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "quality",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Relevance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "relevance",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Timeliness",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "verbose_name_plural": "timeliness",
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="EssentialVariable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "domain",
                    models.IntegerField(
                        choices=[
                            (0, "ATMOSPHERIC"),
                            (1, "OCEANIC"),
                            (2, "TERRESTRIAL"),
                        ]
                    ),
                ),
                (
                    "component",
                    models.IntegerField(
                        choices=[
                            (0, "SURFACE"),
                            (1, "UPPER-AIR"),
                            (2, "COMPOSITION"),
                            (3, "PHYSICS"),
                            (4, "BIOGEOCHEMISTRY"),
                            (5, "BIOLOGY/ECOSYSTEMS"),
                            (6, "HYDROLOGICAL"),
                            (7, "CRYOSPHERE"),
                            (8, "CRYOSPHERE/BIOSPHERE"),
                            (9, "BIOSPHERE"),
                            (10, "HUMAN DIMENSION"),
                        ]
                    ),
                ),
                ("parameter", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField()),
                ("link", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
    ]
