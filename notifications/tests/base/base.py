import datetime

from django.test import TestCase
from . import factories


class BaseTest(TestCase):

    def setUp(self):
        user = factories.UserFactory(is_staff=True)
        self.client.force_login(user)
