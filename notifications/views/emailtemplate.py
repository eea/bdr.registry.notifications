import csv
import json

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
    format_body,
    format_subject,
    set_values_for_parameters,
)
from notifications.models import Cycle

from notifications.models import (
    CycleEmailTemplate,
    CycleNotification,
    Company,
    CompaniesGroup,
    EmailTemplate,
    Person,
    Stage,
)
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class CycleEmailTemplateBase(NotificationsBaseView):
    model = CycleEmailTemplate

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateBase, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
                        kwargs={'pk': self.object.stage.cycle.pk}),
                'Reporting cycle for year {}'.format(self.object.stage.cycle)),
            Breadcrumb(
                reverse('notifications:template:view',
                        kwargs={'pk': self.object.pk}),
                self.object),
        ])
        return breadcrumbs

    def get_recipients(self, company_ids=None):
        qs = Person.objects.filter(
            company__group=self.object.group
        )
        if company_ids is not None:
            qs = qs.filter(company__external_id__in=company_ids)
        qs = qs.prefetch_related('company')
        return qs

    def get_recipient_companies(self, company_ids=None):
        qs = Company.objects.filter(
            group=self.object.group
        ).order_by("name")
        if company_ids is not None:
            qs = qs.filter(external_id__in=company_ids)
        return qs


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


class CycleEmailTemplateTriggerDetail(CycleEmailTemplateBase, generic.TemplateView):
    template_name = 'notifications/template/trigger.html'
    http_method_names = ["get", "post"]

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateTriggerDetail, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Trigger'),
        ])
        return breadcrumbs

    def get_company_ids(self):
        if 'csv_file' not in self.request.FILES:
            return None
        reader = csv.reader(self.request.FILES["csv_file"].read().decode().splitlines())
        return [row[0] for row in reader if row]

    def get_number_of_emails_to_send(self, companies):
        emails_count = 0
        for company in companies:
            emails_count += company.users.all().count()
        return emails_count

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTriggerDetail, self).get_context_data(**kwargs)
        company_ids = self.get_company_ids()
        context['template'] = self.object
        context['form'] = CycleEmailTemplateTriggerForm()
        companies = self.get_recipient_companies(company_ids)
        context['companies'] = companies.prefetch_related('users')
        if self.object.is_triggered:
            context['companies'] = Company.objects.filter(
                notifications__emailtemplate=self.object
            ).prefetch_related('users').distinct()
            context['recipients'] = context['companies']
        else:
            context['recipients'] = context['companies']
            context['no_of_emails'] = self.get_number_of_emails_to_send(companies)

        context['recipient_json'] = json.dumps([r.id for r in context['recipients']])


        context["companies_filtered"] = False
        if company_ids is not None:
            found_companies = set(map(lambda x: x[0], companies.values_list("external_id")))
            not_found = list(set(company_ids).difference(found_companies))
            context["companies_filtered"] = True
            context["not_found_companies"] = not_found

        return context

    def get_notifications(self):
        return (CycleNotification.objects
                .filter(emailtemplate=self.object)
                .order_by('-sent_date'))

    def get(self, request, *args, **kwargs):
        self.object = CycleEmailTemplate.objects.get(pk=kwargs["pk"])
        return render(request, self.template_name, context=self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.object = CycleEmailTemplate.objects.get(pk=kwargs["pk"])
        return render(request, self.template_name, context=self.get_context_data(**kwargs))


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
        companies = Company.objects.filter(id__in=json.loads(self.request.POST['recipients']))
        form.send_emails(self.get_object(), companies)
        return super(CycleEmailTemplateTriggerSend, self).form_valid(form)


class CycleEmailTemplateTrigger(View):

    def get(self, request, *args, **kwargs):
        view = CycleEmailTemplateTriggerDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "recipients" in self.request.POST:
            view = CycleEmailTemplateTriggerSend.as_view()
        else:
            view = CycleEmailTemplateTriggerDetail.as_view()
        return view(request, *args, **kwargs)


class CycleEmailTemplateTest(CycleEmailTemplateBase, generic.FormView):
    form_class = CycleEmailTemplateTestForm
    template_name = 'notifications/template/test.html'
    success_message = 'Emails were successfully sent'

    def get_object(self):
        obj = get_object_or_404(CycleEmailTemplate,
                                id=self.kwargs['pk'])
        if obj.is_triggered:
            raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTest, self).get_context_data(**kwargs)
        template = self.get_object()
        company = self.request.GET.get('company_name')
        person = self.request.GET.get('person_name')
        if company and person:
            company = Company.objects.filter(name=company).first()
            person = Person.objects.filter(name=person).first()
            context['sent'] = True
        else:
            company = (
                Company.objects
                    .filter(group=template.group)
                    .order_by('?').first()
            )
            if not company:
                context["info"] = "The database does not provide any company for this obligation."
                return context
            person = company.users.order_by('?').first()
        context['company'] = company
        context['person'] = person

        # TODO Create a function that takes param values, body_html and returns the formatted text
        params = set_values_for_parameters(person, company)
        body = template.body_html
        template.body_html = body.format(**params)
        subject = template.subject
        template.subject = subject.format(**params)
        context['params'] = params
        context['template'] = template

        return context

    def get_success_url(self):
        query_args = "?company_name={company}&person_name={person}".format(
            company=self.request.POST['company'],
            person=self.request.POST['contact']
        )
        return reverse('notifications:template:test',
                       args=[self.object.pk]) + query_args

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
            context['person'],
            self.get_company()
        )
        context['template'].subject = format_subject(
            context['template'].subject,
            context['person'],
            self.get_company()
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

    def get_cycle_notification_template(self, stage_code, company, person):
        email_template = EmailTemplate.objects.get(
            group=company.group,
            stage__code=stage_code
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

    def get_context_data(self, **kwargs):
        context = super(NotificationsBaseView, self).get_context_data(**kwargs)

        company = self.get_company()
        context['company'] = company
        context['cycles'] = Cycle.objects.all()
        return context
