import sys

from django import forms
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.db import transaction

from django_q.tasks import async, result

from bdr.settings import EMAIL_SENDER
from .models import Cycle, CycleEmailTemplate, Person, CycleNotification


def make_messages(persons, emailtemplate):
    emails = []
    subject = emailtemplate.subject
    for person in persons:
        company = person.company.first()
        """
          Modify company model to record their repxx fields.
        """
        params = dict(
            REPVAT='',
            REPNAME='',
            REPCOUNTRY='',
            COUNTRY=company.country,
            COMPANY=company.name,
            CONTACT=person.name,
            VAT=company.vat,
            # XXX: how will these be handled?
            USERID='randomid',
            PASSWORD='supersecure',
        )
        body = emailtemplate.body_html
        email_body = body.format(**params)
        recipient_email = [person.email]

        emails.append((recipient_email, email_body))
        # store sent email
        CycleNotification.objects.create(
            subject=subject,
            email=person.email,
            body_html=email_body,
            emailtemplate=emailtemplate,
        )

    emailtemplate.is_triggered = True
    emailtemplate.save()
    return emails


def send_emails(subject, sender, emails):
    for recipient_email, email_body in emails:
        # TODO Email_body is written as html. Both plain text and
        # html messages should be available from interface.
        if len(sys.argv) > 1 and sys.argv[1] == 'test':  # TESTING
            send_mail(subject, email_body, sender, recipient_email,
                      fail_silently=False, html_message=email_body)
        else:
            async(send_mail, *(subject, email_body, sender, recipient_email,
                               False, email_body))


class CycleAddForm(forms.ModelForm):

    class Meta:
        model = Cycle
        fields = ['year', 'closing_date']
        exclude = ('id', 'stage')

    def save(self, commit=True, *args, **kwargs):
        """ When a new reporting cycle is created, all the necessary
            email templates are autmatically created.
        """
        instance = super(CycleAddForm, self).save(commit=False, *args, **kwargs)
        if commit:
            instance.save()
            instance.create_cycle_templates()
        return instance


class CycleEditForm(forms.ModelForm):

    class Meta:
        model = Cycle
        fields = ['stage', 'closing_date']
        exclude = ('id', 'year')


class CycleEmailTemplateEditForm(forms.ModelForm):

    class Meta:
        model = CycleEmailTemplate
        fields = ['subject', 'body_html']
        exclude = ('id', 'cycle', 'emailtemplate')


class CycleEmailTemplateTestForm(forms.Form):

    email = forms.CharField(validators=[validate_email])

    def send_email(self, emailtemplate):
        # send email using the self.cleaned_data dictionary
        subject = emailtemplate.subject
        body_html = emailtemplate.body_html

        email = [self.data['email'].strip()]
        values = {}
        for param in emailtemplate.get_parameters():
            values[param] = self.data[param.lower()]

        body_html = body_html.format(**values)

        send_emails(subject, EMAIL_SENDER, [(email, body_html)])


class CycleEmailTemplateTriggerForm(forms.Form):

    def send_emails(self, emailtemplate):
        with transaction.atomic() as atomic:
            recipients = Person.objects.filter(
                company__group=emailtemplate.group).distinct()
            subject = emailtemplate.subject
            sender = EMAIL_SENDER
            emails_to_send = make_messages(recipients, emailtemplate)
            send_emails(subject, sender, emails_to_send)
