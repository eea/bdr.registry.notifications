import logging
import sys

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.conf import settings

from notifications import (
    FGASES_GROUP_CODE,
    FGASES_EU_GROUP_CODE,
    FGASES_NONEU_GROUP_CODE,
    FGASES_EU,
    BDR_GROUP_CODE
)
from notifications.models import Company, Person, CompaniesGroup
from notifications.registries import FCSRegistry, BDRRegistry
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb
from notifications.tests.base.registry_mock import (
    FCSRegistryMock,
    BDRRegistryMock
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ActionsView(NotificationsBaseView, generic.TemplateView):
    template_name = 'notifications/actions.html'

    def breadcrumbs(self):
        breadcrumbs = super(ActionsView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:actions:home'),
                'Actions'),
        ])
        return breadcrumbs


class ActionsBaseView(generic.View):
    """ Base class for registry actions.
    """

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


class ActionsBaseFCSView(ActionsBaseView):
    """ Handles FCS registry fetching.
    """
    company_path = settings.FGASES_COMPANY_PATH
    person_path = settings.FGASES_PERSON_PATH
    success_msg = ''
    error_msg = ''

    def cleanup(self):
        """ Delete all persons and companies fetched from FCS registry.
        """
        Person.objects.filter(
            company__group__code__in=FGASES_GROUP_CODE
        ).delete()
        Company.objects.filter(
            group__code__in=FGASES_GROUP_CODE
        ).delete()

    def get(self, request, *args, **kwargs):
        if len(sys.argv) > 1 and sys.argv[1] == 'test':  # TESTING
            registry = FCSRegistryMock()
        else:
            registry = FCSRegistry()

        group_eu = CompaniesGroup.objects.get(code=FGASES_EU_GROUP_CODE)
        group_noneu = CompaniesGroup.objects.get(code=FGASES_NONEU_GROUP_CODE)

        # fetch companies
        counter_companies = 0
        errors_companies = []

        for item in registry.get_companies(self.company_path):
            if item['address']['country']['type'] == FGASES_EU:
                group = group_eu
            else:
                group = group_noneu

            company_data = dict(
                external_id=item['company_id'],
                name=item['name'],
                vat=item['vat'],
                country=item['address']['country']['name'],
                group=group
            )

            try:
                company_obj = self.create_company(**company_data)

                username_list = [user["username"] for user in item["users"]]
                persons = Person.objects.filter(
                    username__in=username_list
                )
                company_obj.user.add(*persons)
                counter_companies += 1
            except IntegrityError as e:
                logger.info('Skipped company: %s (%s)', item['name'], e)
                errors_companies.append((e, item['name']))

        # fetch persons
        counter_persons = 0
        errors_persons = []
        for person in registry.get_persons(self.person_path):

            fmt_person_name = '{first_name} {last_name}'
            person_name = fmt_person_name.format(**person)

            person_data = dict(
                username=person['username'],
                name=person_name,
                email=person['email'],
            )

            self.create_person(**person_data)
            counter_persons += 1

        if errors_persons:
            msg = self.error_msg
            msg = msg.format(errors_persons)
        else:
            msg = (
                self.success_msg +
                ' {} companies, {} persons'
            )
            msg = msg.format(counter_companies, counter_persons)

        messages.add_message(request, messages.INFO, msg)

        return redirect('notifications:actions:home')

class ActionsFGasesView(ActionsBaseFCSView):
    """ Handles FGases registry fetching.
    """
    company_path = settings.FGASES_COMPANY_PATH
    person_path = settings.FGASES_PERSON_PATH
    success_msg = 'FGases registry fetched successfully:'
    error_msg = 'FGases registry fetched with errors: {}'


class ActionsODSView(ActionsBaseFCSView):
    """ Handles ODS registry fetching.
    """
    company_path = settings.ODS_COMPANY_PATH
    person_path = settings.ODS_PERSON_PATH
    success_msg = 'ODS registry fetched successfully:'
    error_msg = 'ODS registry fetched with errors: {}'


class ActionsBDRView(ActionsBaseView):
    """ Handles BDR registry fetching.
    """

    def cleanup(self):
        """ Delete all persons and companies fetched from BDR registry.
        """
        Person.objects.filter(
            company__group__code=BDR_GROUP_CODE
        ).delete()
        Company.objects.filter(
            group__code=BDR_GROUP_CODE
        ).delete()

    def get(self, request, *args, **kwargs):
        if len(sys.argv) > 1 and sys.argv[1] == 'test':  # TESTING
            registry = BDRRegistryMock()
        else:
            registry = BDRRegistry()

        group = CompaniesGroup.objects.get(code=BDR_GROUP_CODE)

        # fetch companies
        company_count = 0
        for idx_company, item in enumerate(registry.get_companies(), start=1):

            if item['userid'] is None:
                print item

            company_data = dict(
                external_id=item['userid'],
                name=item['name'],
                vat=item['vat_number'],
                country=item['country_name'],
                group=group
            )

            self.create_company(**company_data)
            company_count += 1

        # fetch persons
        person_count = 0
        errors_persons = []
        for person in registry.get_persons():

            person_data = dict(
                username=person['userid'],
                name=person['contactname'],
                email=person['contactemail'],
            )

            try:
                person_obj = self.create_person(**person_data)
                companies = Company.objects.filter(
                    name=person['companyname'],
                    country=person['country'],
                )
                person_obj.company.add(*companies)
                person_count += 1
            except IntegrityError as e:
                logger.info('Skipped person: %s (%s)', person['userid'], e)
                errors_persons.append((e, person['userid']))

        if errors_persons:
            msg = 'BDR registry fetched with errors: {}'
            msg = msg.format(errors_persons)
        else:
            msg = 'BDR registry fetched successfully: {} companies, {} persons'
            msg = msg.format(company_count, person_count)

        messages.add_message(request, messages.INFO, msg)

        return redirect('notifications:actions:home')
