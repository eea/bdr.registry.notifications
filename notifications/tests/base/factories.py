from datetime import datetime

from factory import SubFactory, RelatedFactory, Sequence
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

from notifications import models


class StageFactory(DjangoModelFactory):

    title = 'StageTest'
    code = Sequence(lambda n: 'code{0}'.format(n))

    class Meta:
        model = models.Stage


class CompaniesGroupFactory(DjangoModelFactory):

    title = 'CompaniesGroupTest'
    code = Sequence(lambda n: 'code{0}'.format(n))

    class Meta:
        model = models.CompaniesGroup


class CompanyFactory(DjangoModelFactory):
    name = 'CompanyName'
    group = SubFactory(CompaniesGroupFactory)

    class Meta:
        model = models.Company


class PersonFactory(DjangoModelFactory):
    username = Sequence(lambda n: 'person{0}'.format(n))
    name = Sequence(lambda n: 'Person name {0}'.format(n))
    email = Sequence(lambda n: 'person{0}.test.com'.format(n))
    company = RelatedFactory(CompanyFactory)

    class Meta:
        model = models.Person


class EmailTemplateFactory(DjangoModelFactory):
    subject = 'EmailTemplateTest'
    group = SubFactory(CompaniesGroupFactory)
    stage = SubFactory(StageFactory)

    class Meta:
        model = models.EmailTemplate


class CycleFactory(DjangoModelFactory):
    stage = SubFactory(StageFactory)
    closing_date = datetime.now()

    class Meta:
        model = models.Cycle


class CycleEmailTemplateFactory(DjangoModelFactory):
    subject = 'CycleEmailTemplateTest'
    cycle = SubFactory(CycleFactory)
    emailtemplate = SubFactory(EmailTemplateFactory)

    class Meta:
        model = models.CycleEmailTemplate

    @staticmethod
    def create_email_template(group=None, stage=None):
        group = group or CompaniesGroupFactory()
        stage = stage or StageFactory()
        emailtemplate = EmailTemplateFactory(
            group=group,
            stage=stage
        )
        return emailtemplate


class CycleNotification(DjangoModelFactory):
    subject = 'CycleNotificationTest'
    emailtemplate = SubFactory(EmailTemplateFactory)


class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: 'user{0}'.format(n))

    class Meta:
        model = User
