from django.test import TestCase
from . import factories


class BaseTest(TestCase):

    BODY_FORMAT = 'Email company {COMPANY} for person {CONTACT}.'

    def setUp(self):
        user = factories.UserFactory(is_staff=True)
        self.client.force_login(user)

    def generate_body_for_person(self, params):
        return self.BODY_FORMAT.format(**params)

    def prepare_email_testing(self):
        self.stage = factories.StageFactory()
        self.group = factories.CompaniesGroupFactory()
        self.cycle = factories.CycleFactory(stage=self.stage)
        self.emailtemplate = factories.EmailTemplateFactory(
            subject='Email template subject',
            body_html=self.BODY_FORMAT,
            group=self.group,
            stage=self.stage
        )
        self.cycle_template = factories.CycleEmailTemplateFactory(
            cycle=self.cycle,
            subject='Cycle email template subject',
            body_html=self.BODY_FORMAT,
            emailtemplate=self.emailtemplate
        )
        self.company = factories.CompanyFactory(group=self.group)
        self.persons = [
            factories.PersonFactory(),
            factories.PersonFactory(),
            factories.PersonFactory()
        ]
        for person in self.persons:
            person.company.add(self.company)
