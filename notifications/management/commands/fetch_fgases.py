import logging

from django.core.management.base import BaseCommand

from notifications import FGASES_EU_GROUP_CODE, FGASES_NONEU_GROUP_CODE, FGASES_EU
from notifications.management.commands.fetch import BaseFetchCommand
from notifications.models import CompaniesGroup
from notifications.registries import FGasesRegistry
from notifications.tests.base.registry_mock import FGasesRegistryMock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseFetchCommand, BaseCommand):
    """ Helpful command to be executed by a cron to fetch new companies from FGASES
    """

    help = 'Fetch companies from FGASES'
    registry = FGasesRegistry
    test_registry = FGasesRegistryMock

    def __init__(self):
        super(Command, self).__init__()
        self.group_eu = CompaniesGroup.objects.get(code=FGASES_EU_GROUP_CODE)
        self.group_noneu = CompaniesGroup.objects.get(code=FGASES_NONEU_GROUP_CODE)

    def get_group(self, company):
        if company['address']['country']['type'] == FGASES_EU:
            return self.group_eu
        return self.group_noneu

    def parse_company_data(self, company):
        return dict(
            external_id=company['company_id'],
            name=company['name'],
            vat=company['vat'],
            country=company['address']['country']['name'],
            group=self.get_group(company))

    def parse_person(self, person):
        fmt_person_name = '{contact_firstname} {contact_lastname}'
        print(person)
        person_name = fmt_person_name.format(**person)
        person_data = dict(
            username=person['username'],
            name=person_name,
            email=person['contact_email'],
        )
        self.create_person(**person_data)
