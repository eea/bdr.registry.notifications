# Generated by Django 2.2.24 on 2021-06-22 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0009_personcompany_current"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalcycle",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalcycleemailtemplate",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="company",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="notifications.CompaniesGroup",
            ),
        ),
        migrations.AlterField(
            model_name="cycle",
            name="year",
            field=models.PositiveSmallIntegerField(default=2021, unique=True),
        ),
        migrations.AlterField(
            model_name="cyclenotification",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="notifications",
                to="notifications.Company",
            ),
        ),
        migrations.AlterField(
            model_name="cyclenotification",
            name="emailtemplate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="emails",
                to="notifications.CycleEmailTemplate",
            ),
        ),
        migrations.AlterField(
            model_name="cyclenotification",
            name="person",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="notifications",
                to="notifications.Person",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcycle",
            name="year",
            field=models.PositiveSmallIntegerField(db_index=True, default=2021),
        ),
    ]