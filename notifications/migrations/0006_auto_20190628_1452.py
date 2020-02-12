# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-28 14:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_add status to company'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='emailtemplate',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='group',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='stage',
        ),
        migrations.DeleteModel(
            name='EmailTemplate',
        ),
    ]