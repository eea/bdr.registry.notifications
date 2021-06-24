from django.urls import reverse

from notifications.tests.base import factories
from notifications.tests.base.base import BaseTest


class DashboardTest(BaseTest):
    def test_dashboard_list(self):
        cycle1 = factories.CycleFactory(year=2016)
        cycle2 = factories.CycleFactory(year=2017)
        resp = self.client.get(reverse("notifications:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["object_list"]), 2)
        self.assertEqual(resp.context["object_list"][0], cycle2)
        self.assertEqual(resp.context["object_list"][1], cycle1)
