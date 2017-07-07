from django.core.urlresolvers import reverse
from django.contrib import auth
from django.test import TestCase


from insitu.tests import base

class UserAuthenticationTests(TestCase):

    required_fields = ['username', 'password']
    REQUIRED_ERROR = ['This field is required.']

    def setUp(self):
        super().setUp()
        self.user = base.UserFactory(username='Test_user')

        self._DATA = {
            'username': self.user.username,
            'password': self.user.password,
        }

        self.errors = {field: self.REQUIRED_ERROR for field in self.required_fields}

    def test_login_no_data(self):
        resp = self.client.post(reverse('auth:login'), {})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(resp.context['form'].errors, self.errors)

    def test_user_login_successful(self):
        resp = self.client.post(reverse('auth:login'), self._DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.user.is_authenticated())

    def test_logout(self):
        self.client.get(reverse('auth:logout'))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
