from django.urls import reverse
from django.core import mail

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest
from notifications.models import CycleNotification


class CycleEmailTemplateTest(BaseTest):
    def setUp(self):
        super(CycleEmailTemplateTest, self).setUp()

        self._EDIT_DATA = {
            'subject': 'Subject Test',
            'body_html': 'Body Test'
        }

    def test_cycle_email_template_view(self):
        stage = factories.StageFactory(can_edit=True)
        cycle = factories.CycleFactory(stage=stage)
        emailtemplate = factories.CycleEmailTemplateFactory.create_email_template()
        cycle_email_template = factories.CycleEmailTemplateFactory(
            emailtemplate=emailtemplate,
            cycle=cycle
        )
        resp = self.client.get(
            reverse('notifications:template:view',
                    kwargs={'pk': cycle_email_template.pk}),
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], cycle_email_template)

    def test_cycle_edit(self):
        stage = factories.StageFactory(can_edit=True)
        cycle = factories.CycleFactory(stage=stage)
        emailtemplate = factories.CycleEmailTemplateFactory.create_email_template()
        cycle_email_template = factories.CycleEmailTemplateFactory(
            emailtemplate=emailtemplate,
            cycle=cycle
        )
        resp = self.client.post(
            reverse('notifications:template:edit',
                    kwargs={'pk': cycle_email_template.pk}),
            self._EDIT_DATA,
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'].subject,
                         self._EDIT_DATA['subject'])
        self.assertEqual(resp.context['object'].body_html,
                         self._EDIT_DATA['body_html'])

    def test_cycle_email_test(self):
        self.stage = factories.StageFactory()
        self.group = factories.CompaniesGroupFactory()
        self.cycle = factories.CycleFactory(stage=self.stage)
        self.emailtemplate = factories.EmailTemplateFactory(
            subject=self._EDIT_DATA['subject'],
            body_html=self._EDIT_DATA['body_html'],
            group=self.group,
            stage=self.stage
        )
        self.cycle_template = factories.CycleEmailTemplateFactory(
            cycle=self.cycle,
            subject=self._EDIT_DATA['subject'],
            body_html=self._EDIT_DATA['body_html'],
            emailtemplate=self.emailtemplate
        )
        self.company = factories.CompanyFactory(group=self.group)
        self.persons = [
            factories.PersonFactory(),
            factories.PersonFactory(),
            factories.PersonFactory()
        ]
        for person in self.persons:
            person.company.add(self.company)

        resp = self.client.post(
            reverse('notifications:template:test',
                    kwargs={'pk': self.cycle_template.pk}),
            self._EDIT_DATA,
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['template'].body_html, self._EDIT_DATA['body_html'])
        self.assertEqual(resp.context['template'].subject, self._EDIT_DATA['subject'])

    def test_cycle_email_test_objects(self):
        self.prepare_email_testing()
        resp = self.client.post(
            reverse('notifications:template:test',
                    kwargs={'pk': self.cycle_template.pk}),
            follow=True
        )

        self.assertEqual(self.company, resp.context['company'])
        self.assertEqual(self.cycle_template, resp.context['template'])
        self.assertIn(resp.context['person'], self.persons)

    def test_cycle_email_trigger(self):
        self.prepare_email_testing()
        resp = self.client.post(
            reverse('notifications:template:trigger',
                    kwargs={'pk': self.cycle_template.pk}),
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        sent_mails = mail.outbox
        i = 0
        cycle_notifications = CycleNotification.objects.all()
        for person in self.persons:
            body_expected = self.generate_body_for_person({
                'CONTACT': person.name,
                'COMPANY': person.company.first().name
            })
            self.assertEqual(sent_mails[i].to[0], person.email)
            self.assertEqual(sent_mails[i].body, body_expected)
            self.assertEqual(cycle_notifications[i].body_html, body_expected)
            self.assertEqual(cycle_notifications[i].counter, 1)
            i += 1
        self.assertEqual(len(cycle_notifications), 3)

    def test_cycle_email_trigger_objects(self):
        self.prepare_email_testing()
        resp = self.client.post(
            reverse('notifications:template:trigger',
                    kwargs={'pk': self.cycle_template.pk}),
            follow=True
        )

        self.assertIn(self.company, resp.context['companies'])
        self.assertEqual(self.cycle_template, resp.context['template'])
        self.assertEqual(len(self.persons), len(resp.context['recipients']))


class ResendEmailTest(BaseTest):
    def setUp(self):
        super(ResendEmailTest, self).setUp()
        stage = factories.StageFactory(can_edit=True)
        cycle = factories.CycleFactory(stage=stage)
        emailtemplate = factories.CycleEmailTemplateFactory.create_email_template()
        company = factories.CompanyFactory(group=emailtemplate.group)
        self.company = company
        self.person = factories.PersonFactory()
        self.person.company.add(company)
        self.cycle_email_template = factories.CycleEmailTemplateFactory(
            emailtemplate=emailtemplate,
            cycle=cycle
        )

    def test_resend_email_view(self):

        resp = self.client.get(
            reverse('notifications:template:resend',
                    kwargs={
                        'pk': self.cycle_email_template.pk,
                        'pk_company': self.company.pk,
                        'pk_person': self.person.pk,
                    }),
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], self.cycle_email_template)
        self.assertEqual(resp.context['person'], self.person)
        self.assertEqual(resp.context['counter'], 0)

    def test_resend_email_trigger(self):
        resp = self.client.post(
            reverse('notifications:template:resend',
                    kwargs={
                        'pk': self.cycle_email_template.pk,
                        'pk_company': self.company.pk,
                        'pk_person': self.person.pk,
                    }),
            follow=True
        )
        notification = CycleNotification.objects.filter(
            email=self.person.email,
            emailtemplate=self.cycle_email_template
        )
        self.assertTrue(notification)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(notification.first().counter, 1)
        self.assertEqual(len(mail.outbox), 1)
