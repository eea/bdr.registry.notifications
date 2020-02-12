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
        cycle = factories.CycleFactory()
        stage = factories.StageFactory(cycle=cycle)
        cycle_email_template = factories.CycleEmailTemplateFactory(
            subject='Test view cycle email template',
            stage=stage
        )
        resp = self.client.get(
            reverse('notifications:template:view',
                    kwargs={'pk': cycle_email_template.pk}),
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], cycle_email_template)

    def test_cycle_edit(self):
        cycle = factories.CycleFactory()
        stage = factories.StageFactory(cycle=cycle)
        cycle_email_template = factories.CycleEmailTemplateFactory(
            subject='Test edit cycle',
            stage=stage
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
        self.cycle = factories.CycleFactory()
        self.stage = factories.StageFactory(cycle=self.cycle)
        self.group = factories.CompaniesGroupFactory(code='vans')
        self.cycle_email_template = factories.CycleEmailTemplateFactory(
            subject=self._EDIT_DATA['subject'],
            body_html=self._EDIT_DATA['body_html'],
            group=self.group,
            stage=self.stage
        )

        self.company = factories.CompanyFactory(group=self.group)
        self.persons = [
            factories.PersonFactory(),
            factories.PersonFactory(),
            factories.PersonFactory()
        ]
        for person in self.persons:
            factories.PersonCompanyFactory(person=person, company=self.company)


        resp = self.client.post(
            reverse('notifications:template:test',
                    kwargs={'pk': self.cycle_email_template.pk}),
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
            {'recipients': str([self.company.id])},
            follow=True,
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
            {'recipients': str([self.company.id])},
            follow=True
        )

        self.assertIn(self.company, resp.context['companies'])
        self.assertEqual(self.cycle_template, resp.context['template'])
        self.assertEqual(
            len(self.persons),
            len(resp.context['recipients'].first().active_users)
        )
