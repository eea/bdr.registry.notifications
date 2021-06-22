import logging

from django.db.models import Q

from notifications.models import Person, Company

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseFetchCommand:

    test_registry = None
    registry = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            dest="test",
            default=False,
            help="Fetch test data",
        )

    def get_registry(self, options):
        if options["test"]:  # TESTING
            return self.test_registry()
        return self.registry()

    def cleanup(self, code):
        """Delete all persons and companies existing"""
        Person.objects.filter(company__group__code=code).delete()
        Company.objects.filter(group__code=code).delete()

    def create_company(self, **kwargs):
        """Create or update a company."""

        name = kwargs["name"]
        external_id = kwargs["external_id"]

        company, created = Company.objects.update_or_create(
            external_id=external_id, defaults=kwargs
        )

        if created:
            logger.info("Fetched company %s (%s)", name, external_id)
        else:
            logger.info("Updated company %s %s (%s)", company.id, name, external_id)

        return company

    def create_person(self, **kwargs):
        """Create or update a person."""
        name = kwargs["name"]
        username = kwargs["username"]
        email = kwargs["email"]

        # XXX This will not catch duplicates
        person = Person.objects.filter(
            Q(email=email)
            | Q(username=username)
            | Q(username=email)
            | Q(email=username)
        ).first()

        if person:
            person.email = email
            person.name = name
            person.save()
            created = False
        else:
            person, created = Person.objects.update_or_create(
                username=username, email=email, defaults=kwargs
            )
        if created:
            logger.info("Fetched person %s (%s)", name, username)
        else:
            logger.info("Updated person %s %s (%s)", person.id, name, username)

        return person

    def parse_person_data(self, person):
        """Custom way of creating a person"""
        raise NotImplementedError

    def parse_company_data(self, company):
        """Custom way of creating a company"""
        raise NotImplementedError

    def get_group(self, company):
        """Custom way of picking a group"""
        raise NotImplementedError

    def fetch_companies(self, registry):
        company_count = 0
        for item in registry.get_companies():
            parsed_company_data = self.parse_company_data(item)
            if parsed_company_data:
                self.create_company(**parsed_company_data)
                company_count += 1
        return company_count

    def fetch_persons(self, registry):
        person_count = 0
        for person in registry.get_persons():
            self.create_person(**self.parse_person_data(person))
            person_count += 1
        return person_count

    def handle(self, *args, **options):
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
