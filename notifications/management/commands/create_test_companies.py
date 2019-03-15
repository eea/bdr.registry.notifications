from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from notifications.models import *


class Command(BaseCommand):
    help = 'Generates some test companies and people.'

    def handle(self, *args, **options):
        call_command('loaddata', 'companiesgroups.json')
        for group in CompaniesGroup.objects.all():
            for i in range(100):
                try:
                    company = Company.objects.create(
                        external_id="%s-%s" % (group.code, i),
                        name="%s Comp-%s" % (group.code, i),
                        group=group,
                        country="ABC",
                        vat="No VAT",
                    )
                    company.save()
                    for j in range(5):
                        person = Person.objects.create(
                            username="%s Comp-%s User %s" % (group.code, i, j),
                            company=company,
                            email="%s-%s-%s@example.com" % (group.code, i, j)
                        )
                        person.save()
                except IntegrityError:
                    continue
