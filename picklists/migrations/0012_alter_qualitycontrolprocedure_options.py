# Generated by Django 3.2.20 on 2023-12-15 13:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("picklists", "0011_update_verbose_plural_names"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="qualitycontrolprocedure",
            options={
                "ordering": ["sort_order"],
                "verbose_name_plural": "Quality control procedures",
            },
        ),
    ]
