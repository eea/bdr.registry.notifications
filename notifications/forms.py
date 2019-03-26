from django import forms
from django.conf import settings
from django.core.mail import get_connection
from django.core.validators import validate_email
from django.db import transaction
from django.forms import ModelChoiceField
from django.utils.html import strip_tags

from django_q.tasks import async

from bdr.settings import EMAIL_SENDER, BCC
from notifications import ACCEPTED_PARAMS
from notifications.models import Stage
from .models import (
    Company,
    Cycle,
    CycleEmailTemplate,
    CycleNotification,
    Person,
)
from .mail_send import send_mail


def set_values_for_parameters(emailtemplate, person, company):
    params = {}
    for param, value in ACCEPTED_PARAMS.items():
        if value:
            params[param] = eval(value)
        else:
            params[param] = value
    return params


def format_body(emailtemplate, person, company):
    params = set_values_for_parameters(emailtemplate, person, company)
    email_body = emailtemplate.body_html.format(**params)
    return email_body


def format_subject(emailtemplate, person, company):
    params = set_values_for_parameters(emailtemplate, person, company)
    subject = emailtemplate.subject.format(**params)
    return subject


def make_messages(companies, emailtemplate):
    emails = []
    notifications = []
    for company in companies:
        for person in company.users.all():
            subject = format_subject(emailtemplate, person, company)
            email_body = format_body(emailtemplate, person, company)
            recipient_email = [person.email]

            emails.append((subject, recipient_email, email_body))

            # store sent email
            notifications.append(CycleNotification(
                subject=subject,
                email=person.email,
                body_html=email_body,
                emailtemplate=emailtemplate,
                person=person,
                company=company
            ))

    CycleNotification.objects.bulk_create(notifications)
    return emails


def send_emails(sender, emailtemplate, companies=None, is_test=False, data=None):
    with transaction.atomic() as atomic:
        bcc = BCC
        if companies:
            sender = EMAIL_SENDER
            emails = make_messages(companies, emailtemplate)
        elif is_test:
            company = Company.objects.filter(name=data.get('company')).first()
            person = Person.objects.filter(name=data.get('contact')).first()
            values = set_values_for_parameters(emailtemplate, person, company)
            email = [data['email'].strip()]
            body_html = emailtemplate.body_html.format(**values)
            subject = emailtemplate.subject.format(**values)
            emails = [(subject, email, body_html)]
            bcc = None
        else:
            recipients = Company.objects.filter(
                group=emailtemplate.group)
            sender = EMAIL_SENDER
            emails = make_messages(recipients, emailtemplate)

    connection = get_connection()
    for subject, recipient_email, email_body in emails:
        plain_html = strip_tags(email_body)
        email_message = send_mail(
            subject, plain_html, sender, recipient_email,
            fail_silently=True,
            bcc=bcc, html_message=email_body,
            connection=connection)

    try:
        connection.close()
    except:
        pass

    if not is_test:
        emailtemplate.status = emailtemplate.SENT
        emailtemplate.save()


def send_mail_sender(task):
    # TODO implement mail
    print("Done")


class CycleAddForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['year', 'closing_date']
        exclude = ('id',)


class CustomModelChoiceField(ModelChoiceField):
    """Workaround for https://code.djangoproject.com/ticket/30014"""

    def to_python(self, value):
        if isinstance(value, self.queryset.model):
            value = getattr(value, self.to_field_name or 'pk')
        return super().to_python(value)


class StageAddForm(forms.ModelForm):
    cycle = CustomModelChoiceField(Cycle.objects.all(), disabled=True)

    class Meta:
        model = Stage
        fields = ['cycle', 'title']

    def __init__(self, *args, **kwargs):
        super(StageAddForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "Name"

    def save(self, commit=True, *args, **kwargs):
        """When a new stage is added to a cycle create a template
        for each group.
        """
        kwargs['commit'] = False
        instance = super().save(*args, **kwargs)
        if commit:
            instance.save()
            instance.create_stage_templates()
        return instance


class CycleEmailTemplateEditForm(forms.ModelForm):
    class Meta:
        model = CycleEmailTemplate
        fields = ['subject', 'body_html']
        exclude = ('id', 'cycle', 'emailtemplate')

    def __init__(self, *args, **kwargs):
        super(CycleEmailTemplateEditForm, self).__init__(*args, **kwargs)
        self.fields['subject'].label = "Email subject"
        self.fields['body_html'].label = "Email body"

class CycleEmailTemplateTestForm(forms.Form):
    email = forms.CharField(validators=[validate_email])

    def send_email(self, emailtemplate):
        if not settings.ASYNC_EMAILS:  # TESTING
            send_emails(EMAIL_SENDER, emailtemplate, is_test=True, data=self.data)
        else:
            async(send_emails, *(EMAIL_SENDER, emailtemplate, None, True, self.data),
                  hook='notifications.forms.send_mail_sender')


class CycleEmailTemplateTriggerForm(forms.Form):

    def send_emails(self, emailtemplate, companies):
        emailtemplate.status = emailtemplate.PROCESSING
        emailtemplate.save()

        if not settings.ASYNC_EMAILS:  # TESTING
            send_emails(EMAIL_SENDER, emailtemplate, companies)
            emailtemplate.status = emailtemplate.SENT
            emailtemplate.save()
        else:
            async(send_emails, *(EMAIL_SENDER, emailtemplate, companies),
                  hook='notifications.forms.send_mail_sender')


class ResendEmailForm(forms.Form):

    def send_email(self, emailtemplate, person):
        send_emails(EMAIL_SENDER, emailtemplate, [person])
