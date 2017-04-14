from datetime import datetime

from django import forms
from django.core.validators import validate_email
from django.core.mail import send_mail

from .models import Cycle, CycleEmailTemplate


class CycleAddForm(forms.ModelForm):

    class Meta:
        model = Cycle
        fields = ['year', 'closing_date']
        exclude = ('id', 'stage')

    def save(self, commit=True, *args, **kwargs):
        """ When a new reporting cycle is created, all the necessary
            notifications are autmatically created.
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
        fields = ['subject', 'body_html', 'body_text']
        exclude = ('id', 'cycle', 'emailtemplate')


class CycleEmailTemplateTestForm(forms.Form):

    email = forms.CharField(validators=[validate_email])

    def send_email(self, emailtemplate):
        # send email using the self.cleaned_data dictionary
        subject = emailtemplate.subject
        body_html = emailtemplate.body_html
        body_text = emailtemplate.body_text

        email = self.data['email'].strip()
        values = {}
        for param in emailtemplate.get_parameters():
            value = self.data[param.lower()]
            values[param] = value

        body_html = body_html.format(**values)
        body_text = body_html.format(**values)

        send_mail(
            subject,
            body_text,
            'FROM@example.com',
            [email],
            fail_silently=False,
            html_message=body_html
        )
