# Generated by Django 3.2.23 on 2024-02-22 09:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("picklists", "0012_alter_qualitycontrolprocedure_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="code",
            field=models.CharField(max_length=3, primary_key=True, serialize=False),
        ),
    ]
