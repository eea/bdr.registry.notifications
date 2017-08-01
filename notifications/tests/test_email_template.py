from django.test import TestCase
from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


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
