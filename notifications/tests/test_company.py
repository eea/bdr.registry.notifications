from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


class CompanyTest(BaseTest):

    def test_company_list(self):
        group = factories.CompaniesGroupFactory(code='f-gases-eu')
        company = factories.CompanyFactory(group=group)
        resp = self.client.get(reverse('notifications:companies'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['groups']), 1)
        self.assertEqual(resp.context['items'][0], company)


class SentNotificationsTest(BaseTest):

    def test_sent_notification(self):
        group = factories.CompaniesGroupFactory()
        company = factories.CompanyFactory(group=group)
        stage = factories.StageFactory(can_edit=True)
        cycle = factories.CycleFactory(stage=stage)
        emailtemplate = factories.EmailTemplateFactory(group=group,
                                                       stage=stage)
        cycle_emailtemplate = factories.CycleEmailTemplateFactory(emailtemplate=emailtemplate,
                                                                  cycle=cycle)

        resp = self.client.get(
            reverse('notifications:template:sent_notifications',
                    kwargs={
                        'pk': cycle_emailtemplate.pk,
                        'pk_company': company.pk,
                    })
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['company'], company)
        self.assertEqual(len(resp.context['persons_info']), 0)
