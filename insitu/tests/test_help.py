from django.core.urlresolvers import reverse
from insitu.tests import base
import unittest


class HelpTests(base.FormCheckTestCase):

    def test_help_get(self):
        base.UpdateFrequencyFactory()
        self.client.force_login(self.creator)
        base.BarrierFactory()
        resp = self.client.get(reverse('help'))
        self.assertEqual(resp.status_code, 200)

    def test_crash_me_not_accesible_by_normal_user(self):
        self.client.force_login(self.creator)
        resp = self.client.get(reverse('crashme'))
        self.assertEqual(resp.status_code, 200)

    @unittest.expectedFailure
    def test_crash_me(self):
        user = base.UserFactory(username='admin', is_superuser=True)
        self.client.force_login(user)
        self.client.get(reverse('crashme'))
