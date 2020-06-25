import csv
import json
import random
from urllib.parse import urlencode

from django.contrib.postgres.search import SearchVector
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from notifications import BDR_GROUP_CODES, ECR_GROUP_CODES
from notifications.forms import (
    CycleEmailTemplateEditForm,
    CycleEmailTemplateTestForm,
    CycleEmailTemplateTriggerForm,
    set_values_for_parameters,
)
from notifications.models import Cycle

from notifications.models import (
    CycleEmailTemplate,
    CycleNotification,
    Company,
    CompaniesGroup,
    Person,
    PersonCompany,
)
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb

class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context

class CycleEmailTemplateBase(NotificationsBaseView):
    model = CycleEmailTemplate

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateBase, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:cycle:view',
                        kwargs={'pk': self.object.stage.cycle.pk}),
                'Reporting cycle for {}'.format(self.object.stage.cycle)),
            Breadcrumb(
                reverse('notifications:template:view',
                        kwargs={'pk': self.object.pk}),
                'Email template for {}'.format(self.object.group.title )),
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
        ).order_by("name").prefetch_related('personcompany_set')
        if company_ids is not None:
            qs = qs.filter(external_id__in=company_ids)
        return qs


class CycleEmailTemplateView(CycleEmailTemplateBase, generic.DetailView):
    template_name = 'notifications/template/view.html'
    context_object_name = 'template'


class CycleEmailTemplateEdit(CycleEmailTemplateBase, generic.UpdateView):
    form_class = CycleEmailTemplateEditForm
    template_name = 'notifications/template/edit.html'
    success_message = 'Email template saved succesfully.'
    context_object_name = 'template'


    def get_initial(self):
        old_template_id = self.request.GET.get('old_template', None)
        try:
            old_template =  CycleEmailTemplate.objects.get(id=old_template_id)
            initial = {
                'subject': old_template.subject,
                'body_html': old_template.body_html,
            }
        except:
            return {}
        return initial

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateEdit, self).get_context_data(**kwargs)
        last_2_cycles_ids = [ cycle.id for cycle in Cycle.objects.order_by('-closing_date')[:2]]
        old_templates = CycleEmailTemplate.objects.filter(
            status=CycleEmailTemplate.SENT,
            stage__cycle_id__in=last_2_cycles_ids
        ).order_by('group__title')
        context['old_templates'] = old_templates
        return context

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
            Breadcrumb('', 'Edit email template'),
        ])
        return breadcrumbs


class CycleEmailTemplateTriggerDetail(CycleEmailTemplateBase, generic.TemplateView):
    template_name = 'notifications/template/trigger.html'
    http_method_names = ["get", "post"]

    def breadcrumbs(self):
        breadcrumbs = super(CycleEmailTemplateTriggerDetail, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Filter/Send emails'),
        ])
        return breadcrumbs

    def get_company_ids(self):
        if 'csv_file' not in self.request.FILES:
            return None
        reader = csv.reader(self.request.FILES["csv_file"].read().decode("utf-8-sig").splitlines())
        return [row[0] for row in reader if row]

    def get_number_of_emails_to_send(self, companies):
        emails_count = 0
        for company in companies:
            emails_count += len(company.personcompany_set.all())
        return emails_count

    def get_context_data(self, **kwargs):
        context = super(CycleEmailTemplateTriggerDetail, self).get_context_data(**kwargs)
        company_ids = self.get_company_ids()
        context['template'] = self.object
        context['form'] = CycleEmailTemplateTriggerForm()
        companies = self.get_recipient_companies(company_ids)
        context['companies'] = companies
        if self.object.is_triggered:
            context['companies'] = Company.objects.filter(
                notifications__emailtemplate=self.object
            )
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


class CycleEmailTemplateTriggerNotificationsJson(JSONResponseMixin, TemplateView):
    template_name = 'notifications/template/json.html'
    http_method_names = ["post",]

    def get_number_of_emails_to_send(self, companies):
        emails_count = 0
        for company in companies:
            emails_count += len(company.personcompany_set.all())
        return emails_count

    def get_recipient_companies(self, company_ids=None):
        qs = Company.objects.filter(
            group=self.object.group
        ).order_by("name").prefetch_related('personcompany_set')
        if company_ids is not None:
            qs = qs.filter(id__in=company_ids)
        return qs

    def get_sort(self, order, direction):
        if self.object.group.code in BDR_GROUP_CODES:
            sorting = ['external_id', 'name', 'personcompany__person__name', 'personcompany__person__email']
        else:
            sorting = ['integer_external_id', 'name', 'personcompany__person__name', 'personcompany__person__email']
        if direction == 'desc':
            return '-' + sorting[order]
        return sorting[order]

    def get_companies_ecr(self, companies, order):
        return companies.filter(personcompany__current=True).values_list('external_id', 'name',
            'personcompany__person__name', 'personcompany__person__email').extra(
            select={
                'integer_external_id': 'CAST(external_id AS INTEGER)',
                'lower_name':'lower(name)',
                'lower_personcompany__person__name': 'personcompany__person__name',
                'lower_personcompany__person__email': 'personcompany__person__email'
            }).order_by(order)

    def get_companies_bdr(self, companies, order):
        return companies.filter(personcompany__current=True).values_list('external_id', 'name',
            'personcompany__person__name', 'personcompany__person__email').extra(
            select={
                'integer_external_id': 'external_id',
                'lower_name':'lower(name)',
                'lower_personcompany__person__name': 'personcompany__person__name',
                'lower_personcompany__person__email': 'personcompany__person__email'
            }).order_by(order)

    def get_data(self, context):
        order = self.request.POST.get('order[0][column]')
        direction = self.request.POST.get('order[0][dir]')
        search_value = self.request.POST.get('search[value]')
        self.object = CycleEmailTemplate.objects.get(id=self.kwargs['pk'])
        order = self.get_sort(int(order), direction)

        if self.object.is_triggered:
            companies = Company.objects.filter(notifications__emailtemplate=self.object).all().prefetch_related('personcompany_set')
        companies = self.get_recipient_companies(self.request.POST.getlist('filtered_companies[]', None))
        if self.object.group.code in BDR_GROUP_CODES:
            companies = self.get_companies_bdr(companies, order)
        else:
            companies = self.get_companies_ecr(companies, order)

        if search_value:
            companies = companies.annotate(search=SearchVector(
                'external_id', 'name', 'personcompany__person__name', 'personcompany__person__email')).filter(search__contains=search_value).distinct()
        start = int(self.request.POST.get('start', 0))
        length = int(self.request.POST.get('length', 10))

        return {
            "recordsTotal": len(companies),
            "recordsFiltered": len(companies),
            "data": list(companies[start:start + length])
        }

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class CycleEmailTemplateTest(CycleEmailTemplateBase, generic.FormView):
    form_class = CycleEmailTemplateTestForm
    template_name = 'notifications/template/test.html'
    success_message = 'Test email was succesfully sent.'

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
            length_active_users = len(company.active_users)
            rand = random.randint(0, length_active_users - 1)
            person = company.active_users[rand]
        context['company'] = company
        context['person'] = person

        # TODO Create a function that takes param values, body_html and returns the formatted text
        params = set_values_for_parameters(template, person, company)
        body = template.body_html
        template.body_html = body.format(**params)
        subject = template.subject
        template.subject = subject.format(**params)
        context['params'] = params
        context['template'] = template

        return context

    def get_success_url(self):
        params = {
            "company_name": self.request.POST['company'],
            "person_name": self.request.POST['contact'],
        }
        query_string = urlencode(params)
        return reverse('notifications:template:test',
                       args=[self.object.pk]) + '?' +  query_string

    def breadcrumbs(self):
        self.object = self.get_object()
        breadcrumbs = super(CycleEmailTemplateTest, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb('', 'Test email template'),
        ])
        return breadcrumbs

    def form_valid(self, form):
        self.object = self.get_object()
        form.send_email(self.object)
        return super(CycleEmailTemplateTest, self).form_valid(form)


class ViewSentNotificationForCompany(NotificationsBaseView, generic.DetailView):
    template_name = 'notifications/template/sent_notifications.html'
    email_template_id_list = []

    def breadcrumbs(self):
        breadcrumbs = super(ViewSentNotificationForCompany, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(reverse('notifications:companies'), 'Statistics'),
            Breadcrumb('', '{}'.format(self.get_company().name)),
        ])
        return breadcrumbs

    def get_object(self):
        return get_object_or_404(CompaniesGroup,
                                 id=self.kwargs['pk'])

    def get_company(self):
        return get_object_or_404(Company,
                                 id=self.kwargs['pk_company'],
                                 group=self.get_object())

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
