# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-14 11:36
from __future__ import unicode_literals

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompaniesGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('code', models.SlugField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cycle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=2017, unique=True)),
                ('closing_date', models.DateField()),
            ],
            options={
                'verbose_name_plural': '> Cycles',
            },
        ),
        migrations.CreateModel(
            name='CycleEmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('body_html', ckeditor.fields.RichTextField()),
                ('body_text', models.TextField(blank=True, default='', null=True)),
                ('is_triggered', models.BooleanField(default=False)),
                ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.Cycle')),
            ],
            options={
                'verbose_name_plural': '> Cycles email templates',
            },
        ),
        migrations.CreateModel(
            name='CycleNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('email', models.CharField(db_index=True, max_length=128)),
                ('body_html', models.TextField()),
                ('body_text', models.TextField()),
                ('sent_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('emailtemplate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.CycleEmailTemplate')),
            ],
            options={
                'verbose_name_plural': '> Cycles notifications',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('body_html', ckeditor.fields.RichTextField()),
                ('body_text', models.TextField(blank=True, default='', null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.CompaniesGroup')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalCycle',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(db_index=True, default=2017)),
                ('closing_date', models.DateField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical cycle',
            },
        ),
        migrations.CreateModel(
            name='HistoricalCycleEmailTemplate',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('body_html', ckeditor.fields.RichTextField()),
                ('body_text', models.TextField(blank=True, default='', null=True)),
                ('is_triggered', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('cycle', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='notifications.Cycle')),
                ('emailtemplate', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='notifications.EmailTemplate')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical cycle email template',
            },
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('code', models.SlugField(max_length=64, unique=True)),
                ('can_edit', models.BooleanField(default=False)),
                ('can_trigger', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='historicalcycle',
            name='stage',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='notifications.Stage'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='stage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='notifications.Stage'),
        ),
        migrations.AddField(
            model_name='cycleemailtemplate',
            name='emailtemplate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.EmailTemplate'),
        ),
        migrations.AddField(
            model_name='cycle',
            name='stage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='notifications.Stage'),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplate',
            unique_together=set([('group', 'stage')]),
        ),
        migrations.AlterUniqueTogether(
            name='cyclenotification',
            unique_together=set([('email', 'emailtemplate')]),
        ),
    ]
