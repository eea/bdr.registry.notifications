import json

from django.core.management import call_command

from notifications import models
from notifications.tests.base.base import BaseTest


class FgasesActionTest(BaseTest):
    fixtures = ['companiesgroups.json', ]

    def test_fgases(self):
        call_command('fetch_fgases', '--test')

        # Check companies
        companies = models.Company.objects.all()
        json_data = open('notifications/tests/base/json/fgas_companies.json')
        companies_data = json.load(json_data)
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies.first().name, companies_data[0]['name'])
        self.assertEqual(companies.last().name, companies_data[1]['name'])

        # Check persons
        persons = models.Person.objects.all()
        json_data = open('notifications/tests/base/json/fgas_persons.json')
        persons_data = json.load(json_data)
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons.first().username, persons_data[0]['username'])

        # Check relation
        for person_data in persons_data:
            fmt_person_name = '{contact_firstname} {contact_lastname}'
            person_name = fmt_person_name.format(**person_data)
            person = models.Person.objects.get(
                username=person_data['username'],
                name=person_name,
                email=person_data['contact_email'],
            )
            self.assertIn(
                person_data['companyname'],
                person.company.values_list('name', flat=True)
            )


class BDRActionTest(BaseTest):
    fixtures = ['companiesgroups.json', ]

    def test_fgases(self):
        call_command('fetch_bdr', '--test')

        # Check companies
        companies = models.Company.objects.all()
        json_data = open('notifications/tests/base/json/bdr_companies.json')
        companies_data = json.load(json_data)
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies.first().name, companies_data[0]['name'])
        self.assertEqual(companies.last().name, companies_data[1]['name'])

        # Check persons
        persons = models.Person.objects.all()
        json_data = open('notifications/tests/base/json/bdr_persons.json')
        persons_data = json.load(json_data)
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons.first().name, persons_data[0]['contactname'])

        # Check relation
        for person_data in persons_data:
            person = models.Person.objects.get(
                username=person_data['userid'],
                name=person_data['contactname'],
                email=person_data['contactemail']
            )
            self.assertIn(
                person_data['companyname'],
                person.company.values_list('name', flat=True)
            )
