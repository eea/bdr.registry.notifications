from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views import generic

from notifications.forms import (
    CycleEmailTemplateEditForm,
    CycleEmailTemplateTestForm,
    CycleEmailTemplateTriggerForm
)
from notifications.models import CycleEmailTemplate, CycleNotification, Person
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class CycleEmailTemplateBase(NotificationsBaseView):
    model = CycleEmailTemplate

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateBase, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
                        kwargs={'pk': self.object.cycle.pk}),
                'Reporting cycle for year {}'.format(self.object.cycle)),
            Breadcrumb(
                reverse('notifications:template:view',
                        kwargs={'pk': self.object.pk}),
                self.object),
        ])
        return breadcrumbs

    def get_recipients(self):
        return Person.objects.filter(
            company__group=self.object.group).distinct()


class CycleEmailTemplateView(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/template/view.html'
    context_object_name = 'template'


class CycleEmailTemplateEdit(CycleEmailTemplateBase, generic.UpdateView):
    form_class = CycleEmailTemplateEditForm
    template_name = 'notifications/template/edit.html'
    success_message = 'Reporting cycle notification edited successfully'
    context_object_name = 'template'

    def get_success_url(self):
        return reverse('notifications:template:view',
                       args=[self.object.pk])

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateEdit, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Edit'),
        ])
        return breadcrumbs


class CycleEmailTemplateTriggerDetail(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/template/trigger.html'
    context_object_name = 'template'

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateTriggerDetail, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTriggerDetail, self).get_context_data(**kwargs)
        context['form'] = CycleEmailTemplateTriggerForm()
        context['recipients'] = self.get_recipients()
        context['notifications'] = self.get_notifications()
        return context

    def get_notifications(self):
        return (CycleNotification.objects
                .filter(emailtemplate=self.object)
                .order_by('-sent_date'))


class CycleEmailTemplateTriggerSend(generic.detail.SingleObjectMixin, generic.FormView):
    template_name = 'notifications/template/trigger.html'
    form_class = CycleEmailTemplateTriggerForm
    model = CycleEmailTemplate
    success_message = 'Emails sent successfully!'

    def get_success_url(self):
        return reverse(
            'notifications:template:trigger',
            args=[self.kwargs['pk']]
        )

    def form_valid(self, form):
        form.send_emails(self.get_object())
        return super(CycleEmailTemplateTriggerSend, self).form_valid(form)


class CycleEmailTemplateTrigger(View):

    def get(self, request, *args, **kwargs):
        view = CycleEmailTemplateTriggerDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CycleEmailTemplateTriggerSend.as_view()
        return view(request, *args, **kwargs)


class CycleEmailTemplateTest(CycleEmailTemplateBase, generic.FormView):
    form_class = CycleEmailTemplateTestForm
    template_name = 'notifications/template/test.html'
    success_message = 'Email was send successfully'

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTest, self).get_context_data(**kwargs)
        context['template'] = get_object_or_404(CycleEmailTemplate,
                                        id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('notifications:template:test',
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
