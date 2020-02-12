from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


class PersonTest(BaseTest):

    def test_person_list(self):
        group = factories.CompaniesGroupFactory(code='f-gases-eu')
        company = factories.CompanyFactory(group=group)
        person = factories.PersonFactory()
        factories.PersonCompanyFactory(person=person, company=company)

        person.save()
        resp = self.client.get(reverse('notifications:persons'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['items']), 1)
        self.assertEqual(resp.context['items'][0], person)
