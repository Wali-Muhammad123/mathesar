# Generated by Django 3.1.14 on 2022-01-26 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mathesar', '0025_auto_20211118_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='display_options',
            field=models.JSONField(default=None, null=True),
        ),
    ]
