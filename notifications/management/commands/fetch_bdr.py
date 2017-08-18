import logging

from django.core.management.base import BaseCommand

from notifications import BDR_GROUP_CODE
from notifications.management.commands.fetch import BaseFetchCommand
from notifications.models import CompaniesGroup
from notifications.registries import BDRRegistry
from notifications.tests.base.registry_mock import BDRRegistryMock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseFetchCommand, BaseCommand):
    """ Helpful command to be executed by a cron to fetch new companies from BDR
    """

    help = 'Fetch companies from BDR registry'
    registry = BDRRegistry
    test_registry = BDRRegistryMock

    def __init__(self):
        super(Command, self).__init__()
        self.group = CompaniesGroup.objects.get(code=BDR_GROUP_CODE)

    def get_group(self, company):
        return self.group

    def parse_company_data(self, company):
        return dict(
            external_id=company['userid'],
            name=company['name'],
            vat=company['vat_number'],
            country=company['country_name'],
            group=self.get_group(company)
        )

    def parse_person_data(self, person):
        return dict(
            username=person['userid'],
            name=person['contactname'],
            email=person['contactemail'],
        )