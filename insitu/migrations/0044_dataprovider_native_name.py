# Generated by Django 2.2.24 on 2022-11-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("insitu", "0043_loggedaction_target_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataprovider",
            name="native_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]