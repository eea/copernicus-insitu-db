from django.urls import reverse
from insitu.tests import base


class ReportsTest(base.FormCheckTestCase):
    def test_reports_list(self):
        self.client.force_login(self.creator)
        resp = self.client.get(reverse("reports:list"))
        self.assertEqual(resp.status_code, 200)
