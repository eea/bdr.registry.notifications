from django.http import Http404
from django.shortcuts import get_object_or_404
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


class CycleView(NotificationsBaseView, generic.ListView):
    model = CycleEmailTemplate
    template_name = 'notifications/cycle/view.html'
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        self.cycle = get_object_or_404(Cycle,
                                       id=self.kwargs['pk'])
        return super(CycleView, self).dispatch(request, *args, **kwargs)

    def breadcrumbs(self):
        breadcrumbs = super(CycleView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
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
    template_name = 'notifications/cycle/edit.html'
    success_message = 'Reporting cycle edited successfully'

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

    def get_notifications(self):
        return (CycleNotification.objects
                .filter(emailtemplate__cycle=self.object,
                        emailtemplate__emailtemplate__stage=self.object.stage)
                .order_by('-sent_date'))
