# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-24 19:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cyclenotification",
            name="company",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to="notifications.Company",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="person",
            name="company",
            field=models.ManyToManyField(
                related_name="users", to="notifications.Company"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="cyclenotification",
            unique_together=set([]),
        ),
    ]
