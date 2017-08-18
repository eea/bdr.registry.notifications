import logging

from django.db import IntegrityError

from notifications.models import Person, Company

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseFetchCommand:

    test_registry = None
    registry = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            dest='test',
            default=False,
            help='Fetch test data',
        )

    def get_registry(self, options):
        if options['test']:  # TESTING
            return self.test_registry()
        return self.registry()

    def cleanup(self, code):
        """ Delete all persons and companies existing
        """
        Person.objects.filter(
            company__group__code=code
        ).delete()
        Company.objects.filter(
            group__code=code
        ).delete()

    def create_company(self, **kwargs):
        """ Create or update a company.
        """
        name = kwargs['name']
        external_id = kwargs['external_id']

        company, created = Company.objects.update_or_create(
            external_id=external_id,
            defaults=kwargs
        )

        if created:
            logger.info('Fetched company %s (%s)', name, external_id)
        else:
            logger.info(
                'Updated company %s %s (%s)', company.id, name, external_id)

        return company

    def create_person(self, **kwargs):
        """ Create or update a company.
        """
        name = kwargs['name']
        username = kwargs['username']

        person, created = Person.objects.update_or_create(
            username=username,
            defaults=kwargs
        )

        if created:
            logger.info('Fetched person %s (%s)', name, username)
        else:
            logger.info('Updated person %s %s (%s)', person.id, name, username)

        return person

    def parse_person(self, person):
        """ Custom way of creating a person """
        raise NotImplemented

    def parse_company_data(self, company):
        """ Custom way of creating a company """
        raise NotImplemented

    def get_group(self, company):
        """ Custom way of picking a group """
        raise NotImplemented

    def handle(self, *args, **options):
        registry = self.get_registry(options)

        # fetch companies
        company_count = 0
        for company in registry.get_companies():
            self.create_company(
                **self.parse_company_data(company))
            company_count += 1

        # fetch persons
        person_count = 0
        errors_persons = []
        for person in registry.get_persons():
            try:
                self.parse_person(person)
                person_count += 1
            except IntegrityError as e:
                logger.info('Skipped person: %s (%s)', person['userid'], e)
                errors_persons.append((e, person['userid']))

        if errors_persons:
            msg = 'Registry fetched with errors: {}'
            msg = msg.format(errors_persons)
        else:
            msg = 'Registry fetched successfully: {} companies, {} persons'
            msg = msg.format(company_count, person_count)
        print(msg)
