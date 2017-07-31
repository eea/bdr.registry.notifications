import logging

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from notifications import (
    FGASES_GROUP_CODE,
    FGASES_EU_GROUP_CODE,
    FGASES_NONEU_GROUP_CODE,
    FGASES_EU,
    BDR_GROUP_CODE
)
from notifications.models import Company, Person, CompaniesGroup
from notifications.registries import FGasesRegistry, BDRRegistry
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


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


class ActionsFGasesView(ActionsBaseView):
    """ Handles FGases registry fetching.
    """

    def cleanup(self):
        """ Delete all persons and companies fetched from FGases registry.
        """
        Person.objects.filter(
            company__group__code__in=FGASES_GROUP_CODE
        ).delete()
        Company.objects.filter(
            group__code__in=FGASES_GROUP_CODE
        ).delete()

    def get(self, request, *args, **kwargs):
        registry = FGasesRegistry()

        group_eu = CompaniesGroup.objects.get(code=FGASES_EU_GROUP_CODE)
        group_noneu = CompaniesGroup.objects.get(code=FGASES_NONEU_GROUP_CODE)

        # fetch companies
        counter_companies = 0
        for item in registry.get_companies():

            if item['address']['country']['type'] == FGASES_EU:
                group = group_eu
            else:
                group = group_noneu

            self.create_company(
                external_id=item['company_id'],
                name=item['name'],
                vat=item['vat'],
                country=item['address']['country']['name'],
                group=group
            )

            counter_companies += 1

        # fetch persons
        counter_persons = 0
        errors_persons = []
        for person in registry.get_persons():

            fmt_person_name = '{contact_firstname} {contact_lastname}'
            person_name = fmt_person_name.format(**person)

            person_data = dict(
                username=person['username'],
                name=person_name,
                email=person['contact_email'],
            )

            try:
                person_obj = self.create_person(**person_data)
            except IntegrityError as e:
                logger.info('Skipped person: %s (%s)', person['username'], e)
                errors_persons.append((e, person['username']))

            companies = Company.objects.filter(
                name=person['companyname'],
                country=person['country'],
            )

            person_obj.company.add(*companies)
            counter_persons += 1

        if errors_persons:
            msg = 'BDR registry fetched with errors: {}'
            msg = msg.format(errors_persons)
        else:
            msg = (
                'FGases registry fetched successfully:'
                ' {} companies, {} persons'
            )
            msg = msg.format(counter_companies, counter_persons)

        messages.add_message(request, messages.INFO, msg)

        return redirect('notifications:actions:home')


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
        registry = BDRRegistry()

        group = CompaniesGroup.objects.get(code=BDR_GROUP_CODE)

        # fetch companies
        person_count = 0
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

            company = self.create_company(**company_data)

        # fetch persons
        count_persons = 0
        errors_persons = []
        for person in registry.get_persons():

            person_data = dict(
                username=person['userid'],
                name=person['contactname'],
                email=person['contactemail'],
            )

            try:
                person_obj = self.create_person(**person_data)
            except IntegrityError as e:
                logger.info('Skipped person: %s (%s)', person['userid'], e)
                errors_persons.append((e, person['userid']))

            companies = Company.objects.filter(
                name=person['companyname'],
                country=person['country'],
            )

            person_obj.company.add(*companies)
            count_persons += 1

        if errors_persons:
            msg = 'BDR registry fetched with errors: {}'
            msg = msg.format(errors_persons)
        else:
            msg = 'BDR registry fetched successfully: {} companies, {} persons'
            msg = msg.format(idx_company, person_count)

        messages.add_message(request, messages.INFO, msg)

        return redirect('notifications:actions:home')
