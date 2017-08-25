from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest
from notifications.models import Stage


class CompanyTest(BaseTest):

    def test_company_list(self):
        group = factories.CompaniesGroupFactory(code='f-gases-eu')
        company = factories.CompanyFactory(group=group)
        resp = self.client.get(reverse('notifications:companies'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['groups']), 1)
        self.assertEqual(resp.context['items'][0], company)


class SentNotificationsTest(BaseTest):
    fixtures = ['stages.json']

    def test_sent_notification(self):
        group = factories.CompaniesGroupFactory()
        company = factories.CompanyFactory(group=group)
        person1 = factories.PersonFactory()
        person2 = factories.PersonFactory()
        person1.company.add(company)
        person2.company.add(company)
        stages = Stage.objects.all()
        cycle = factories.CycleFactory(stage=stages.first())
        for stage in stages:
            emailtemplate = (
                factories.CycleEmailTemplateFactory.create_email_template(group,
                                                                          stage)
            )
            cycle_emailtemplate = (
                factories.CycleEmailTemplateFactory(emailtemplate=emailtemplate,
                                                    cycle=cycle)
            )

        resp = self.client.get(
            reverse('notifications:template:sent_notifications',
                    kwargs={
                        'pk': group.pk,
                        'pk_company': company.pk,
                    })
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['company'], company)
        self.assertEqual(len(resp.context['persons_info']), 2)
        self.assertEqual(person1, resp.context['persons_info'][0]['person'])
        self.assertEqual(person2, resp.context['persons_info'][1]['person'])
        for i in range(0, 2):
            for stage in resp.context['persons_info'][i]['stages']:
                self.assertFalse(stage['value'])