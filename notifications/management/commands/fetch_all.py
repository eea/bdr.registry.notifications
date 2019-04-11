import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command
from notifications.management.commands.fetch import BaseFetchCommand

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseFetchCommand, BaseCommand):
    """ Command to fetch companies and persons from both BDR and European Registry
    """
    help = 'Fetch companies from BDR and European Registry'

    def handle(self, *args, **options):
        logger.info("Starting fetching companies from BDR registry")
        call_command('fetch_bdr')
        logger.info("Finished fetching companies from BDR registry")

        logger.info("Starting fetching companies from ECR registry")
        call_command('fetch_ecr')
        logger.info("Finished fetching companies from ECR registry")
