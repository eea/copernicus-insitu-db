# Generated by Django 3.2.24 on 2024-03-05 09:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("insitu", "0053_requirement_essential_variables"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="data",
            name="essential_variables",
        ),
    ]
