from factory import SubFactory, RelatedFactory
from factory.django import DjangoModelFactory

from notifications import models


class StageFactory(DjangoModelFactory):

    title = 'StageTest'

    class Meta:
        model = models.Stage


class CompaniesGroupFactory(DjangoModelFactory):

    title = 'CompaniesGroupTest'

    class Meta:
        model = models.CompaniesGroup


class CompanyFactory(DjangoModelFactory):
    name = 'CompanyName'
    group = SubFactory(CompaniesGroupFactory)

    class Meta:
        model = models.Company


class PersonFactory(DjangoModelFactory):
    username = 'PersonTest'
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

    class Meta:
        model = models.Cycle


class CycleEmailTemplateFactory(DjangoModelFactory):
    subject = 'CycleEmailTemplateTest'
    cycle = SubFactory(CycleFactory)
    emailtemplate = SubFactory(EmailTemplateFactory)

    class Meta:
        model = models.CycleEmailTemplate


class CycleNotification(DjangoModelFactory):
    subject = 'CycleNotificationTest'
    emailtemplate = SubFactory(EmailTemplateFactory)
