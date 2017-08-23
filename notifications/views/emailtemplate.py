from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from notifications.forms import (
    CycleEmailTemplateEditForm,
    CycleEmailTemplateTestForm,
    CycleEmailTemplateTriggerForm,
    ResendEmailForm,
    format_body
)

from notifications.models import CycleEmailTemplate, CycleNotification, Person, Company, EmailTemplate, Stage, CompaniesGroup
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

    def get_recipient_companies(self):
        return Company.objects.filter(
            group=self.object.group).distinct().order_by("name")


class CycleEmailTemplateView(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/template/view.html'
    context_object_name = 'template'


class CycleEmailTemplateEdit(CycleEmailTemplateBase, generic.UpdateView):
    form_class = CycleEmailTemplateEditForm
    template_name = 'notifications/template/edit.html'
    success_message = 'Reporting cycle notification edited successfully'
    context_object_name = 'template'

    def get_object(self):
        obj = get_object_or_404(CycleEmailTemplate,
                                id=self.kwargs['pk'])
        if obj.is_triggered:
            raise PermissionDenied

        return obj

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

        companies = self.get_recipient_companies()
        context['companies'] = companies.prefetch_related('user')

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

    def get_object(self):
        obj = get_object_or_404(CycleEmailTemplate,
                                id=self.kwargs['pk'])
        if obj.is_triggered:
            raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTest, self).get_context_data(**kwargs)
        template = self.get_object()
        company = (
            Company.objects
            .filter(group=template.group)
            .order_by('?').first()
        )
        context['company'] = company
        context['person'] = company.user.order_by('?').first()
        context['params'] = template.get_parameters()

        # TODO Create a function that takes param values, body_html and returns the formatted text
        params = dict(
            REPVAT='',
            REPNAME='',
            REPCOUNTRY='',
            COUNTRY=company.country,
            COMPANY=company.name,
            CONTACT=context['person'].name,
            VAT=company.vat,
            # XXX: how will these be handled?
            USERID='randomid',
            PASSWORD='TODO',
        )
        body = template.body_html
        template.body_html = body.format(**params)
        context['template'] = template

        return context

    def get_success_url(self):
        return reverse('notifications:template:test',
                       args=[self.object.pk])

    def breadcrumbs(self):
        self.object = self.get_object()
        breadcrumbs = super(CycleEmailTemplateTest, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Test'),
        ])
        return breadcrumbs

    def form_valid(self, form):
        self.object = self.get_object()
        form.send_email(self.object)
        return super(CycleEmailTemplateTest, self).form_valid(form)


class ResendEmailBase(NotificationsBaseView):
    template_name = 'notifications/template/resend.html'
    model = CycleEmailTemplate

    def get_company(self):
        company = get_object_or_404(Company,
                                    id=self.kwargs['pk_company'])
        return company


class ResendEmailDetail(ResendEmailBase, generic.DetailView):
    context_object_name = 'template'

    def breadcrumbs(self):
        breadcrumbs = super(ResendEmailDetail, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(ResendEmailDetail, self).get_context_data(**kwargs)
        context['person'] = get_object_or_404(
            Person,
            pk=self.kwargs['pk_person'],
            company__group=context['template'].group,
            company=self.get_company()
        )
        context['template'].body_html = format_body(
            context['template'].body_html,
            context['person']
        )
        cycle_notification = CycleNotification.objects.filter(
            email=context['person'].email,
            emailtemplate=context['template']
        ).first()
        if cycle_notification:
            context['counter'] = cycle_notification.counter
        else:
            context['counter'] = 0
        return context


class ResendEmailTrigger(ResendEmailBase, generic.FormView, generic.detail.SingleObjectMixin):
    success_message = 'Email sent successfully!'
    form_class = ResendEmailForm

    def get_object(self):
        return get_object_or_404(CycleEmailTemplate,
                                 id=self.kwargs['pk'])

    def get_person(self):
        return get_object_or_404(Person,
                                 id=self.kwargs['pk_person'],
                                 company__group=self.get_object().group,
                                 company=self.get_company())

    def get_success_url(self):
        return reverse(
            'notifications:template:trigger',
            args=[self.kwargs['pk']]
        )

    def form_valid(self, form):
        form.send_email(self.get_object(), self.get_person())
        return super(ResendEmailTrigger, self).form_valid(form)


class ResendEmail(View):

    def get(self, request, *args, **kwargs):
        view = ResendEmailDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ResendEmailTrigger.as_view()
        return view(request, *args, **kwargs)


class ViewSentNotificationForCompany(NotificationsBaseView, generic.DetailView):
    template_name = 'notifications/template/sent_notifications.html'
    email_template_id_list = []

    def get_object(self):
        return get_object_or_404(CompaniesGroup,
                                 id=self.kwargs['pk'])

    def get_company(self):
        return get_object_or_404(Company,
                                 id=self.kwargs['pk_company'],
                                 group=self.get_object())

    def get_cycle_notification_template(self, stage, company, person):
        email_template = EmailTemplate.objects.get(
            group=company.group,
            stage=Stage.objects.get(code=stage)
        )

        cycle_email_template = CycleEmailTemplate.objects.get(
            emailtemplate=email_template,
            cycle__year=timezone.now().year
        )
        self.email_template_id_list.append(cycle_email_template.id)

        cycle_notification = CycleNotification.objects.filter(
            emailtemplate=cycle_email_template,
            email=person.email
        )

        return cycle_notification

    def verify_cycle_notification(self, cycle_notification):
        if cycle_notification.count() > 0:
            return True
        else:
            return False

    def get_persons_info(self, company, persons):
        persons_info = []

        for person in persons:
            obj = dict()
            obj['person'] = person
            obj['stages'] = []

            for stage_code in Stage.get_main_stages():
                cycle_notification = self.get_cycle_notification_template(stage_code, company, person)
                stage = dict()
                stage['value'] = self.verify_cycle_notification(cycle_notification)
                stage['email_template_id'] = self.email_template_id_list.pop(0)
                obj['stages'].append(stage)

            persons_info.append(obj)

        return persons_info

    def get_context_data(self, **kwargs):
        context = super(NotificationsBaseView, self).get_context_data(**kwargs)

        company = self.get_company()
        persons = company.user.all()
        persons_info = self.get_persons_info(company, persons)

        context['company'] = company
        context['persons_info'] = persons_info

        return context

