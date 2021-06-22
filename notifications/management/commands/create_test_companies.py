from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from notifications.models import Company, CompaniesGroup, Person


class Command(BaseCommand):
    help = "Generates some test companies and people."

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--companies",
            default=100,
            type=int,
            help="Number of companies to generate",
        )
        parser.add_argument(
            "-p",
            "--people",
            default=5,
            type=int,
            help="Number of people to generate per company",
        )

    def handle(self, *args, **options):
        call_command("loaddata", "companiesgroups.json")
        for group in CompaniesGroup.objects.all():
            for i in range(options["companies"]):
                try:
                    company = Company.objects.create(
                        external_id="%s-%s" % (group.code, i),
                        name="%s Comp-%s" % (group.code, i),
                        group=group,
                        country="ABC",
                        vat="No VAT",
                    )
                    company.save()
                    for j in range(options["people"]):
                        person = Person.objects.create(
                            username="%s Comp-%s User %s" % (group.code, i, j),
                            name="%s Comp-%s Name %s" % (group.code, i, j),
                            company=company,
                            email="%s-%s-%s@example.com" % (group.code, i, j),
                        )
                        person.save()
                except IntegrityError:
                    continue
