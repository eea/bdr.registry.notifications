# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from collections import namedtuple

from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import logout
from django.contrib import messages

from braces import views as braces_views

from . import (FGASES_EU, FGASES_NONEU,
               FGASES_EU_GROUP_CODE, FGASES_NONEU_GROUP_CODE, FGASES_GROUP_CODE,
               BDR_GROUP_CODE)
from .models import (CompaniesGroup, Company, Person, Cycle,
                     CycleEmailTemplate, CycleNotification, STAGE_CLOSED)
from .forms import (CycleAddForm, CycleEditForm,
                    CycleEmailTemplateEditForm, CycleEmailTemplateTestForm)
from .registries import BDRRegistry, FGasesRegistry


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


Breadcrumb = namedtuple('Breadcrumb', ['url', 'title'])


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'You have been logged out.')
    return redirect('notifications:dashboard')


class NotificationsBaseView(braces_views.StaffuserRequiredMixin,
                            SuccessMessageMixin):

    login_url = '/accounts/login'

    def breadcrumbs(self):
        return [
            Breadcrumb(settings.BDR_SERVER_URL, 'BDR'),
            Breadcrumb(reverse('notifications:dashboard'),
                       'Registries Notifications')
        ]


class DashboardView(NotificationsBaseView, generic.ListView):
    model = Cycle
    template_name = 'notifications/dashboard.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Cycle.objects.order_by('-year')

    def can_initiate_new_cycle(self):
        r = True
        cycles = Cycle.objects.order_by('-year')
        if len(cycles) > 0:
            last_cycle = cycles[0]
            if last_cycle.stage.pk != STAGE_CLOSED:
                r = False
        return r


class CycleAdd(NotificationsBaseView, generic.CreateView):
    model = Cycle
    form_class = CycleAddForm
    template_name = 'notifications/cycle_add.html'
    success_message = 'Reporting cycle added successfully'

    def get_success_url(self):
        return reverse('notifications:dashboard')

    def breadcrumbs(self):
        breadcrumbs = super(CycleAdd, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Add reporting cycle'),
        ])
        return breadcrumbs


class CycleView(NotificationsBaseView, generic.ListView):
    model = CycleEmailTemplate
    template_name = 'notifications/cycle_view.html'
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        self.cycle = get_object_or_404(Cycle,
                                       id=self.kwargs['pk'])
        return super(CycleView, self).dispatch(request,
                                                        *args,
                                                        **kwargs)

    def breadcrumbs(self):
        breadcrumbs = super(CycleView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle_view',
                        kwargs={'pk': self.cycle.pk}),
                'Reporting cycle for year {}'.format(self.cycle)),
        ])
        return breadcrumbs

    def get_queryset(self):
        return (CycleEmailTemplate.objects
                .filter(cycle=self.cycle)
                .order_by('emailtemplate__stage'))


class CycleEdit(NotificationsBaseView, generic.UpdateView):
    model = Cycle
    form_class = CycleEditForm
    template_name = 'notifications/cycle_edit.html'
    success_message = 'Reporting cycle edited successfully'

    def get_object(self, queryset=None):
        obj = super(CycleEdit, self).get_object(queryset)
        if obj.can_edit:
            return obj
        else:
            raise Http404('Not avaiable for edit.')

    def get_success_url(self):
        return reverse('notifications:cycle_view', args=[self.object.pk])

    def breadcrumbs(self):
        kwargs = {'pk': self.object.pk}
        breadcrumbs = super(CycleEdit, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(reverse('notifications:cycle_view', kwargs=kwargs),
                       'Reporting cycle for year {}'.format(self.object)),
            Breadcrumb('', 'Edit'),
        ])
        return breadcrumbs


class CycleTrigger(NotificationsBaseView, generic.DetailView):
    model = Cycle
    template_name = 'notifications/cycle_trigger.html'

    def breadcrumbs(self):
        breadcrumbs = super(CycleTrigger, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle_view',
                        kwargs={'pk': self.object.pk}),
                'Reporting cycle for year {}'.format(self.object)),
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_notifications(self):
        return (CycleNotification.objects
                .filter(emailtemplate__cycle=self.object,
                        emailtemplate__emailtemplate__stage=self.object.stage)
                .order_by('-sent_date'))


class CycleEmailTemplateBase(NotificationsBaseView):
    model = CycleEmailTemplate

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateBase, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle_view',
                        kwargs={'pk': self.object.cycle.pk}),
                'Reporting cycle for year {}'.format(self.object.cycle)),
            Breadcrumb(
                reverse('notifications:emailtemplate_view',
                        kwargs={'pk': self.object.pk}),
                self.object),
        ])
        return breadcrumbs


class CycleEmailTemplateView(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/emailtemplate_view.html'


class CycleEmailTemplateEdit(CycleEmailTemplateBase, generic.UpdateView):
    form_class = CycleEmailTemplateEditForm
    template_name = 'notifications/emailtemplate_edit.html'
    success_message = 'Reporting cycle notification edited successfully'

    def get_success_url(self):
        return reverse('notifications:emailtemplate_view',
                       args=[self.object.pk])

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateEdit, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Edit'),
        ])
        return breadcrumbs


class CycleEmailTemplateTrigger(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/emailtemplate_trigger.html'

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateTrigger, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_notifications(self):
        return (CycleNotification.objects
                .filter(emailtemplate=self.object)
                .order_by('-sent_date'))


class CycleEmailTemplateTest(CycleEmailTemplateBase, generic.FormView):
    form_class = CycleEmailTemplateTestForm
    template_name = 'notifications/emailtemplate_test.html'
    success_message = 'Email was send successfully'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(CycleEmailTemplate,
                                       id=self.kwargs['pk'])
        return super(CycleEmailTemplateTest, self).dispatch(request,
                                                        *args,
                                                        **kwargs)

    def get_success_url(self):
        return reverse('notifications:emailtemplate_test',
                       args=[self.object.pk])

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateTest, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Test'),
        ])
        return breadcrumbs

    def form_valid(self, form):
        form.send_email(self.object)
        return super(CycleEmailTemplateTest, self).form_valid(form)


class CompaniesView(NotificationsBaseView, generic.TemplateView):
    template_name = 'notifications/companies.html'

    def breadcrumbs(self):
        breadcrumbs = super(CompaniesView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:companies'),
                'Companies'),
        ])
        return breadcrumbs

    def get_groups(self):
        return CompaniesGroup.objects.all()


class PersonsView(NotificationsBaseView, generic.TemplateView):
    template_name = 'notifications/persons.html'

    def bdr_get_persons(self):
        return Person.objects.all()

    def breadcrumbs(self):
        breadcrumbs = super(PersonsView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:persons'),
                'Persons'),
        ])
        return breadcrumbs


class ActionsView(NotificationsBaseView, generic.TemplateView):
    template_name = 'notifications/actions.html'

    def breadcrumbs(self):
        breadcrumbs = super(ActionsView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:actions'),
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

        #fetch companies
        counter_companies = 0
        for item in registry.get_companies():

            if item['address']['country']['type'] == FGASES_EU:
                group = group_eu
            else:
                group = group_noneu

            self.create_company(external_id=item['company_id'],
                                name=item['name'],
                                vat=item['vat'],
                                country=item['address']['country']['name'],
                                group=group)

            counter_companies += 1

        #fetch persons
        counter_persons = 0

        messages.add_message(request,
                             messages.INFO,
                             ('FGases registry fetched successfully: '
                              '{} companies, {} persons'
                              .format(counter_companies, counter_persons)))
        return redirect('notifications:actions')


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

        return redirect('notifications:actions')
