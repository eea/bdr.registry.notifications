from django.urls import reverse
from django.views import generic

from notifications.forms import CycleAddForm
from notifications.models import Cycle, CycleEmailTemplate
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
