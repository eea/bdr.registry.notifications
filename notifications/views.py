# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import logout
from django.contrib import messages

from braces import views as braces_views

from .models import Cycle, CycleEmailTemplate, CycleNotification, STAGE_CLOSED
from .forms import (CycleAddForm, CycleEditForm,
                    CycleEmailTemplateEditForm, CycleEmailTemplateTestForm)
from .registries import BDRRegistry, FGasesRegistry


Breadcrumb = namedtuple('Breadcrumb', ['url', 'title'])


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'You have been logged out.')
    return redirect('notifications:dashboard')


class NotificationsBaseView(braces_views.StaffuserRequiredMixin,
                            SuccessMessageMixin):

    login_url = '/notifications/accounts/login'

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

    def test_get_companies(self):
        bdr = BDRRegistry()
        fgases = FGasesRegistry()
        return {
            bdr.name: bdr.get_companies(),
            fgases.name: fgases.get_companies()
        }


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
