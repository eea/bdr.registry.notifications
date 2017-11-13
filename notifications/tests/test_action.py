import json

from django.core.management import call_command

from notifications import models
from notifications.tests.base.base import BaseTest


class ECRActionTest(BaseTest):
    fixtures = ['companiesgroups.json', ]

    def test_ecr(self):
        call_command('fetch_ecr', '--test')

        # Check companies
        companies = models.Company.objects.all()
        json_data = open('notifications/tests/base/json/ecr_companies.json')
        companies_data = json.load(json_data)
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies.first().name, companies_data[0]['name'])
        self.assertEqual(companies.last().name, companies_data[1]['name'])

        # Check persons
        persons = models.Person.objects.all()
        json_data = open('notifications/tests/base/json/ecr_persons.json')
        persons_data = json.load(json_data)
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons.first().username, persons_data[0]['username'])

        # Check relation
        for company_data in companies_data:
            company = models.Company.objects.get(
                external_id=company_data['company_id'],
                name=company_data['name'],
                vat=company_data['vat'],
                country=company_data['address']['country']['name']
            )
            for person_data in company_data['users']:
                person = models.Person.objects.get(email=person_data['email'])
                self.assertIn(company, person.company.all())


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
