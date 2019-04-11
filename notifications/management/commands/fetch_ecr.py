import logging

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from notifications import (
    FGASES_EU_GROUP_CODE, FGASES_NONEU_GROUP_CODE, ODS_GROUP_CODE,
    FGASES_EU, FGASES_NONEU,
)
from notifications.management.commands.fetch import BaseFetchCommand
from notifications.models import CompaniesGroup, Person, Company
from notifications.registries import EuropeanCacheRegistry
from notifications.tests.base.registry_mock import EuropeanCacheRegistryMock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseFetchCommand, BaseCommand):
    """ Helpful command to be executed by a cron to fetch new companies from ECR
    """

    help = 'Fetch companies from European Cache Registry'
    registry = EuropeanCacheRegistry
    test_registry = EuropeanCacheRegistryMock

    def __init__(self):
        super(Command, self).__init__()
        self.group_eu = CompaniesGroup.objects.get(code=FGASES_EU_GROUP_CODE)
        self.group_noneu = CompaniesGroup.objects.get(code=FGASES_NONEU_GROUP_CODE)
        self.group_ods = CompaniesGroup.objects.get(code=ODS_GROUP_CODE)

    def get_group(self, company):
        if company['domain'] == 'ODS':
            return self.group_ods
        elif company['address']['country']['type'] == FGASES_EU:
            return self.group_eu
        elif company['address']['country']['type'] == FGASES_NONEU:
            return self.group_noneu


    def parse_company_data(self, company):
        representative_name = ''
        representative_vat = ''
        representative_country_name = ''
        if company.get('representative'):
            representative_name = company['representative']['name']
            representative_vat = company['representative']['vatnumber']
            representative_country_name = company['representative']['address']['country']['name']
        return dict(
            external_id=company['company_id'],
            name=company['name'],
            vat=company['vat'],
            country=company['address']['country']['name'],
            group=self.get_group(company),
            status=company['status'],
            representative_name=representative_name,
            representative_vat=representative_vat,
            representative_country_name=representative_country_name
        )

    def parse_person_data(self, person):
        fmt_person_name = '{first_name} {last_name}'
        person_name = fmt_person_name.format(**person)
        return dict(
            username=person['username'],
            name=person_name,
            email=person['email'],
        )

    def check_company_is_valid(self, company):
        if company['status'] == 'VALID':
            return True
        external_id = company['company_id']
        company_obj = Company.objects.really_all().filter(external_id=external_id)
        if company_obj.first():
            company_obj.update(**self.parse_company_data(company))
            logger.info(
                'Company rejected %s (%s)', company_obj.first().name, company_obj.first().external_id)

    def create_company(self, **kwargs):
        """ Create or update a company.
        """
        name = kwargs['name']
        external_id = kwargs['external_id']

        company = Company.objects.really_all().filter(external_id=external_id)
        if company.first():

            company.update(**kwargs)
            company = company.first()
            logger.info(
            'Updated company %s %s (%s)', company.id, name, external_id)
        else:
            company = Company.objects.create(**kwargs)
            logger.info('Fetched company %s (%s)', name, external_id)

        return company

    def fetch_companies(self, registry):
        company_count = 0
        errors = []
        for item in registry.get_companies():
            try:
                if not self.check_company_is_valid(item):
                    continue
                company = self.create_company(
                    **self.parse_company_data(item))
                username_list = [user["username"] for user in item["users"]]
                persons = Person.objects.filter(username__in=username_list)
                company.users.add(*persons)
                company_count += 1
            except IntegrityError as e:
                logger.info('Skipped company: %s (%s)', item['name'], e)
                errors.append((e, item['name']))
        return company_count, errors

    def handle(self, *args, **options):
        registry = self.get_registry(options)
        person_count = self.fetch_persons(registry)
        company_count, errors = self.fetch_companies(registry)

        if errors:
            msg = 'Registry fetched with errors: {}'
            msg = msg.format(errors)
        else:
            msg = 'Registry fetched successfully: {} companies, {} persons'
            msg = msg.format(company_count, person_count)
        logger.info(msg)
