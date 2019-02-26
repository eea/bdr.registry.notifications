import sys
import time

from django import forms
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.db import transaction
from django.utils.html import strip_tags

from django_q.tasks import async, result

from bdr.settings import EMAIL_SENDER
from .models import Cycle, CycleEmailTemplate, Person, CycleNotification


def format_body(body_html, person):
    company = person.company.first()
    """
      Modify company model to record their repxx fields.
    """
    params = dict(
        REPVAT='',
        REPNAME='',
        REPCOUNTRY='',
        EXTERNAL_ID=company.external_id,
        COUNTRY=company.country,
        COMPANY=company.name,
        CONTACT=person.name,
        VAT=company.vat,
        # XXX: how will these be handled?
        USERID='randomid',
        PASSWORD='supersecure',
    )
    body = body_html
    email_body = body.format(**params)
    return email_body

def format_subject(subject, person):
    company = person.company.first()
    params = dict(
        REPVAT='',
        REPNAME='',
        REPCOUNTRY='',
        EXTERNAL_ID=company.external_id,
        COUNTRY=company.country,
        COMPANY=company.name,
        CONTACT=person.name,
        VAT=company.vat,
        # XXX: how will these be handled?
        USERID='randomid',
        PASSWORD='supersecure',
    )
    subject = subject.format(**params)
    return subject

def make_messages(persons, emailtemplate):
    emails = []
    for person in persons:
        subject = format_subject(emailtemplate.subject, person)
        email_body = format_body(emailtemplate.body_html, person)
        recipient_email = [person.email]

        emails.append(( subject ,recipient_email, email_body))

        cycle_notification = CycleNotification.objects.filter(
            email=person.email,
            emailtemplate=emailtemplate
        ).first()

        counter = 1
        if cycle_notification:
            counter = cycle_notification.counter + 1
            cycle_notification.delete()

        # store sent email
        CycleNotification.objects.create(
            subject=subject,
            email=person.email,
            body_html=email_body,
            emailtemplate=emailtemplate,
            counter=counter
        )

    emailtemplate.is_triggered = True
    emailtemplate.save()
    return emails


def send_emails(sender, emailtemplate, person=None):
    with transaction.atomic() as atomic:
        if person:
            subject = emailtemplate.subject
            sender = EMAIL_SENDER
            emails = make_messages([person], emailtemplate)
        else:
            recipients = Person.objects.filter(
                company__group=emailtemplate.group)
            subject = emailtemplate.subject
            sender = EMAIL_SENDER
            emails = make_messages(recipients, emailtemplate)

        for subject, recipient_email, email_body in emails:
            plain_html = strip_tags(email_body)
            send_mail(subject, plain_html, sender, recipient_email,
                      fail_silently=False, html_message=email_body)


def send_mail_sender(task):
    # TODO implement mail
    print("Done")


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


class CycleEmailTemplateEditForm(forms.ModelForm):

    class Meta:
        model = CycleEmailTemplate
        fields = ['subject', 'body_html']
        exclude = ('id', 'cycle', 'emailtemplate')


class CycleEmailTemplateTestForm(forms.Form):

    email = forms.CharField(validators=[validate_email])

    def send_emails(self, sender, emailtemplate):
        # send email using the self.cleaned_data dictionary
        subject = emailtemplate.subject
        body_html = emailtemplate.body_html

        email = [self.data['email'].strip()]
        values = {}
        for param in emailtemplate.get_parameters():
            values[param] = self.data.get(param.lower(), None)

        body_html = body_html.format(**values)
        subject = subject.format(**values)

        for subject, recipient_email, email_body in [(subject, email, body_html)]:
            plain_html = strip_tags(email_body)
            send_mail(subject, plain_html, sender, recipient_email,
                      fail_silently=False, html_message=email_body)

    def send_email(self, emailtemplate):
        if len(sys.argv) > 1 and sys.argv[1] == 'test':  # TESTING
            self.send_emails(EMAIL_SENDER, emailtemplate)
        else:
            async(self.send_emails, *(EMAIL_SENDER, emailtemplate),
                  hook='notifications.forms.send_mail_sender')


class CycleEmailTemplateTriggerForm(forms.Form):

    def send_emails(self, emailtemplate):
        if len(sys.argv) > 1 and sys.argv[1] == 'test':  # TESTING
            send_emails(EMAIL_SENDER, emailtemplate)
        else:
            async(send_emails, *(EMAIL_SENDER, emailtemplate),
                  hook='notifications.forms.send_mail_sender')


class ResendEmailForm(forms.Form):

    def send_email(self, emailtemplate, person):
        send_emails(sender, emailtemplate, person)
