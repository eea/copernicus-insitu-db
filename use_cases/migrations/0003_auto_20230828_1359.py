# Generated by Django 2.2.28 on 2023-08-24 13:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("use_cases", "0002_auto_20230822_1409"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reference",
            name="date",
            field=models.CharField(max_length=256),
        ),
    ]
