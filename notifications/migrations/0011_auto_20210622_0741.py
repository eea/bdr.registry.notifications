# Generated by Django 3.2.4 on 2021-06-22 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0010_auto_20210622_0717"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="check_passed",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="personcompany",
            name="current",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
