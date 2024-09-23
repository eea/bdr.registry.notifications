import logging

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from notifications import BDR_GROUP_CODES
from notifications.management.commands.fetch import BaseFetchCommand
from notifications.models import CompaniesGroup, Company, PersonCompany
from notifications.registries import BDRRegistry
from notifications.tests.base.registry_mock import BDRRegistryMock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseFetchCommand, BaseCommand):
    """Helpful command to be executed by a cron to fetch new companies from BDR"""

    help = "Fetch companies from BDR registry"
    registry = BDRRegistry
    test_registry = BDRRegistryMock

    def __init__(self):
        super(Command, self).__init__()

    def set_all_persons_to_current_false(self):
        persons_companies = PersonCompany.objects.filter(
            company__group__code__in=BDR_GROUP_CODES
        )
        persons_companies.update(current=False)

    def get_group(self, company):
        return CompaniesGroup.objects.get(code=company["obligation"])

    def parse_company_data(self, company):
        if company["obligation"] in BDR_GROUP_CODES:
            return dict(
                external_id=company["userid"],
                name=company["name"],
                vat=company["vat_number"],
                country=company["country_name"],
                group=self.get_group(company),
            )
        else:
            return dict()

    def parse_person_data(self, person):
        for key in person.keys():
            person[key] = person[key]
        return dict(
            username=person["contactemail"],
            name=person["contactname"].replace("None", "").strip(),
            email=person["contactemail"],
        )

    def set_current_user_true(self, person, companies):
        for company in companies:
            try:
                person_company = PersonCompany.objects.really_all().get(
                    company=company, person=person
                )
                person_company.delete()
                person_company = PersonCompany.objects.create(
                    company=company, person=person, current=True
                )
            except PersonCompany.DoesNotExist:
                person_company = PersonCompany.objects.create(
                    company=company, person=person, current=True
                )

    def fetch_persons(self, registry):
        person_count = 0
        errors = []
        for item in registry.get_persons():
            try:
                person = self.create_person(**self.parse_person_data(item))
                person_count += 1
                companies = Company.objects.filter(
                    name=item["companyname"], country=item["country"]
                )
                self.set_current_user_true(person, companies)
            except IntegrityError as e:
                logger.info("Skipped person: %s (%s)", item["contactemail"], e)
                errors.append((e, item["contactemail"]))
        return person_count, errors

    def handle(self, *args, **options):
        self.set_all_persons_to_current_false()
        registry = self.get_registry(options)
        company_count = self.fetch_companies(registry)
        person_count, errors = self.fetch_persons(registry)

        if errors:
            msg = "Registry fetched with errors: {}"
            msg = msg.format(errors)
        else:
            msg = "Registry fetched successfully: {} companies, {} persons"
            msg = msg.format(company_count, person_count)
        logger.info(msg)
        return msg
