from django.core.urlresolvers import reverse
from django.contrib import auth
from django.test import TestCase

from insitu.models import User
from insitu.tests import base


class UserAuthenticationTests(TestCase):

    required_fields = ['username', 'password']
    REQUIRED_ERROR = ['This field is required.']

    def setUp(self):
        super().setUp()
        self._DATA = {
            'username': 'testuser',
            'password': 'secret'
        }
        self.user = User.objects.create_user(**self._DATA)

        self.errors = {field: self.REQUIRED_ERROR for field in
                       self.required_fields}

    def test_login_user_already_logged_in(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('auth:login'), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse('home'))
        self.client.logout()

    def test_login_no_data(self):
        resp = self.client.post(reverse('auth:login'), {})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(resp.context['form'].errors, self.errors)

    def test_user_login_successful(self):
        resp = self.client.post(reverse('auth:login'), self._DATA)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('home'))

    def test_logout(self):
        self.client.get(reverse('auth:logout'))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_get_change_password(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('auth:change_password'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_user_change_password_successful(self):
        self.client.force_login(self.user)
        self.data = {
            'username': 'testuser',
            'old_password': 'secret',
            'new_password1': 'new_password1',
            'new_password2': 'new_password1',
        }
        resp = self.client.post(reverse('auth:change_password'), self.data,
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse('home'))


class UserTeammatesTests(TestCase):

    def setUp(self):
        super().setUp()
        self.creator = base.UserFactory(username='Creator user')
        self.user1 = base.UserFactory(username='User1')
        self.user2 = base.UserFactory(username='User2')
        self._DATA = {
            'teammates': [self.user1.id, self.user2.id]
        }

    def test_get_edit_teammates(self):
        self.client.force_login(self.creator)
        resp = self.client.get(reverse('auth:edit_teammates'))
        self.assertTrue(resp.status_code, 200)

    def test_edit_teammates_error(self):
        self.client.force_login(self.creator)
        self.data = {
            'teammates': [self.creator.id]
        }
        resp = self.client.post(reverse('auth:edit_teammates'), self.data)
        self.assertTrue(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors ==
                        {'__all__': ['You cannot be your own teammate.']})

    def test_edit_teammates_succesfully(self):
        self.client.force_login(self.creator)
        resp = self.client.post(reverse('auth:edit_teammates'), self._DATA)
        self.assertTrue(resp.status_code, 200)
        self.assertTrue([x for x in self.creator.team.teammates.all()]
                        == [self.user1, self.user2])
