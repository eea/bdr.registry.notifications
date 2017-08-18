from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from notifications.forms import CycleAddForm, CycleEditForm
from notifications.models import Cycle, CycleEmailTemplate, CycleNotification
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class CycleAdd(NotificationsBaseView, generic.CreateView):
    model = Cycle
    form_class = CycleAddForm
    template_name = 'notifications/cycle/add.html'
    success_message = 'Reporting cycle added successfully'

    def get_success_url(self):
        return reverse('notifications:dashboard')

    def breadcrumbs(self):
        breadcrumbs = super(CycleAdd, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Add reporting cycle'),
        ])
        return breadcrumbs


class CycleDetailView(NotificationsBaseView, generic.DetailView):
    model = Cycle
    template_name = 'notifications/cycle/view.html'
    context_object_name = 'cycle'

    def breadcrumbs(self):
        cycle = self.object
        breadcrumbs = super(CycleDetailView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
                        kwargs={'pk': cycle.pk}),
                'Reporting cycle for year {}'.format(cycle)),
        ])
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(CycleDetailView, self).get_context_data(**kwargs)
        context['templates'] = (CycleEmailTemplate.objects
            .filter(cycle=self.object)
            .order_by('emailtemplate__group')
            .prefetch_related('emailtemplate__group',
                              'emailtemplate__stage',
                              'cycle')
        )
        context['stages'] = ['Invitations', 'Reminder', 'Deadline', 'After']
        return context


class CycleEdit(NotificationsBaseView, generic.UpdateView):
    model = Cycle
    form_class = CycleEditForm
    template_name = 'notifications/cycle/edit.html'
    success_message = 'Reporting cycle edited successfully'
    context_object_name = 'cycle'

    def get_object(self, queryset=None):
        obj = super(CycleEdit, self).get_object(queryset)
        if obj.can_edit:
            return obj
        else:
            raise Http404('Not avaiable for edit.')

    def get_success_url(self):
        return reverse('notifications:cycle:view', args=[self.object.pk])

    def breadcrumbs(self):
        kwargs = {'pk': self.object.pk}
        breadcrumbs = super(CycleEdit, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(reverse('notifications:cycle:view', kwargs=kwargs),
                       'Reporting cycle for year {}'.format(self.object)),
            Breadcrumb('', 'Edit'),
        ])
        return breadcrumbs


class CycleTrigger(NotificationsBaseView, generic.DetailView):
    model = Cycle
    template_name = 'notifications/cycle/trigger.html'
    context_object_name = 'cycle'

    def breadcrumbs(self):
        breadcrumbs = super(CycleTrigger, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
                        kwargs={'pk': self.object.pk}),
                'Reporting cycle for year {}'.format(self.object)),
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(CycleTrigger, self).get_context_data(**kwargs)
        context['notifications'] = (CycleNotification.objects
            .filter(emailtemplate__cycle=self.object,
                    emailtemplate__emailtemplate__stage=self.object.stage)
            .select_related('emailtemplate__emailtemplate__group')
            .order_by('-sent_date'))
        return context
