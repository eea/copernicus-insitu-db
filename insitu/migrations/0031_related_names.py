# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-11-19 09:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("insitu", "0030_requirement_scale"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="component",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="insitu.Component",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="requirements",
            field=models.ManyToManyField(
                related_name="products",
                through="insitu.ProductRequirement",
                to="insitu.Requirement",
            ),
        ),
        migrations.AlterField(
            model_name="productrequirement",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_requirements",
                to="insitu.Product",
            ),
        ),
        migrations.AlterField(
            model_name="productrequirement",
            name="requirement",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_requirements",
                to="insitu.Requirement",
            ),
        ),
    ]
