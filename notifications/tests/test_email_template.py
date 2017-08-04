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
            i += 1
        self.assertEqual(len(cycle_notifications), 3)
