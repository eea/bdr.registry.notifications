import json

from django.urls import reverse

from notifications import models
from notifications.tests.base.base import BaseTest


class FgasesActionTest(BaseTest):
    fixtures = ['companiesgroups.json', ]

    def test_fgases(self):
        resp = self.client.get(reverse('notifications:actions:fgases'),
                               follow=True)
        self.assertEqual(resp.status_code, 200)
        companies = models.Company.objects.all()
        json_data = open('notifications/tests/base/json/fgas_companies.json')
        companies_data = json.load(json_data)
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies.first().name, companies_data[0]['name'])
        self.assertEqual(companies.last().name, companies_data[1]['name'])
        persons = models.Person.objects.all()
        json_data = open('notifications/tests/base/json/fgas_persons.json')
        persons_data = json.load(json_data)
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons.first().username, persons_data[0]['username'])


class BDRActionTest(BaseTest):
    fixtures = ['companiesgroups.json', ]

    def test_fgases(self):
        resp = self.client.get(reverse('notifications:actions:bdr'),
                               follow=True)
        self.assertEqual(resp.status_code, 200)
        companies = models.Company.objects.all()
        json_data = open('notifications/tests/base/json/bdr_companies.json')
        companies_data = json.load(json_data)
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies.first().name, companies_data[0]['name'])
        self.assertEqual(companies.last().name, companies_data[1]['name'])
        persons = models.Person.objects.all()
        json_data = open('notifications/tests/base/json/bdr_persons.json')
        persons_data = json.load(json_data)
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons.first().name, persons_data[0]['contactname'])
