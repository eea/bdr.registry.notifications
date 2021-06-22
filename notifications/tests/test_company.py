from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


class CompanyTest(BaseTest):
    def test_company_list(self):
        group = factories.CompaniesGroupFactory(code="vans")
        company = factories.CompanyFactory(group=group)
        resp = self.client.get(reverse("notifications:companies"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["groups"]), 1)
        self.assertEqual(resp.context["items"][0], company)


class SentNotificationsTest(BaseTest):
    def test_sent_notification(self):
        group = factories.CompaniesGroupFactory(code="cars")
        company = factories.CompanyFactory(group=group)
        person1 = factories.PersonFactory()
        person2 = factories.PersonFactory()
        factories.PersonCompanyFactory(person=person1, company=company)
        factories.PersonCompanyFactory(person=person2, company=company)

        resp = self.client.get(
            reverse(
                "notifications:template:sent_notifications",
                kwargs={
                    "pk": group.pk,
                    "pk_company": company.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["company"], company)
        self.assertEqual(len(resp.context["company"].active_users), 2)
        self.assertEqual(person1, resp.context["company"].active_users[0])
        self.assertEqual(person2, resp.context["company"].active_users[1])
