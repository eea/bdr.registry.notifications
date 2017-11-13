from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


class CycleTest(BaseTest):
    def setUp(self):
        super(CycleTest, self).setUp()
        self._DATA = {
            'year': 2017,
            'closing_date': '2009-10-03',
        }
        self._EDIT_DATA = {
            'closing_date': '2005-04-03',
        }

    def test_cycle_add(self):
        resp = self.client.post(reverse('notifications:cycle:add'), self._DATA,
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['items']), 1)
        self.assertEqual(resp.context['items'][0].year, self._DATA['year'])
        self.assertEqual(str(resp.context['items'][0].closing_date),
                         self._DATA['closing_date'])

    def test_cycle_view(self):
        stage = factories.StageFactory(can_edit=True)
        cycle = factories.CycleFactory(stage=stage)
        emailtemplate = factories.CycleEmailTemplateFactory.create_email_template()
        cycle_email_template = factories.CycleEmailTemplateFactory(
            emailtemplate=emailtemplate,
            cycle=cycle
        )
        resp = self.client.get(
            reverse('notifications:cycle:view', kwargs={'pk': cycle.pk}),
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], cycle)
        self.assertEqual(len(resp.context['templates']), 1)
        self.assertEqual(resp.context['templates'].first(), cycle_email_template)
        self.assertEqual(resp.context['stages'], ['Invitations', 'Reminder', 'Deadline', 'After'])
