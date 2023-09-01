from django.urls import reverse
from django.contrib import auth
from django.test import TestCase

from insitu.models import User, Data
from insitu.tests import base
from django.core import mail


class UserAuthenticationTests(TestCase):

    required_fields = ["username", "password"]
    REQUIRED_ERROR = ["This field is required."]

    def setUp(self):
        super().setUp()
        self._DATA = {"username": "testuser", "password": "secret"}
        self.user = User.objects.create_user(**self._DATA)

        self.errors = {field: self.REQUIRED_ERROR for field in self.required_fields}

    def test_login_user_already_logged_in(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("auth:login"), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse("about"))
        self.client.logout()

    def test_login_no_data(self):
        resp = self.client.post(reverse("auth:login"), {})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context["form"].errors, {})
        self.assertDictEqual(resp.context["form"].errors, self.errors)

    def test_user_login_successful(self):
        resp = self.client.post(reverse("auth:login"), self._DATA)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("about"))

    def test_logout(self):
        self.client.get(reverse("auth:logout"))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_get_change_password(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("auth:change_password"), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_user_change_password_successful(self):
        self.client.force_login(self.user)
        self.data = {
            "username": "testuser",
            "old_password": "secret",
            "new_password1": "new_password1",
            "new_password2": "new_password1",
        }
        resp = self.client.post(
            reverse("auth:change_password"), self.data, follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse("about"))


class CreateUserTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser(
            username="foobar", email="foo@bar.com", password="barbaz"
        )
        self.client.force_login(user=self.user)

    def test_add_new_user(self):
        new_user = {
            "email": "new_user@test.com",
            "username": "test",
        }
        response = self.client.post(
            reverse("admin:auth_user_add"), new_user, follow=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Set up Copernicus password")


class UserTeammatesTests(TestCase):
    def setUp(self):
        super().setUp()
        self.creator = base.UserFactory(username="Creator user")
        self.user1 = base.UserFactory(username="User1")
        self.user2 = base.UserFactory(username="User2")
        self._DATA = {"requests": [self.user1.id, self.user2.id]}

    def test_get_edit_teammates(self):
        self.client.force_login(self.creator)
        resp = self.client.get(reverse("auth:edit_teammates"))
        self.assertEqual(resp.status_code, 200)

    def test_edit_teammates_error(self):
        self.client.force_login(self.creator)
        self.data = {"requests": [self.creator]}
        resp = self.client.post(reverse("auth:edit_teammates"), self.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["form"].errors["requests"])

    def test_edit_teammates_succesfully(self):
        self.client.force_login(self.creator)
        resp = self.client.post(reverse("auth:edit_teammates"), self._DATA)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            [x for x in self.creator.team.requests.all()], [self.user1, self.user2]
        )
        self.assertEqual([x for x in self.user1.team.requests.all()], [])
        self.assertEqual([x for x in self.user2.team.requests.all()], [])

    def test_edit_teammates_remove_succesfully(self):
        self.client.force_login(self.creator)
        self.client.post(reverse("auth:edit_teammates"), self._DATA)
        self.data = {"requests": [self.user1.id]}
        resp = self.client.post(reverse("auth:edit_teammates"), self.data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual([x for x in self.creator.team.requests.all()], [self.user1])

    def test_edit_teammates_accept_friend_request(self):
        self.client.force_login(self.creator)
        self.client.post(reverse("auth:edit_teammates"), self._DATA)
        self.data = {"requests": [self.user1.id]}
        self.client.post(reverse("auth:edit_teammates"), self.data)
        self.client.force_login(self.user1)
        resp = self.client.get(
            reverse("auth:accept_request", kwargs={"sender_user": self.creator.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.creator, self.user1.team.teammates.all())

    def test_edit_teammates_accept_friend_request_no_permission(self):
        self.client.force_login(self.user1)
        resp = self.client.get(
            reverse("auth:accept_request", kwargs={"sender_user": self.creator.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(self.creator, self.user1.team.teammates.all())

    def test_get_delete_teammate(self):
        self.creator.team.teammates.add(self.user1)
        self.user1.team.teammates.add(self.creator)
        self.client.force_login(self.creator)
        resp = self.client.get(
            reverse("auth:delete_teammate", kwargs={"teammate_id": self.user1.id})
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_delete_teammate_no_permission(self):
        self.client.force_login(self.creator)
        resp = self.client.get(
            reverse("auth:delete_teammate", kwargs={"teammate_id": self.user1.id})
        )
        self.assertEqual(resp.status_code, 200)

    def test_post_delete_teammate_no_permission(self):
        self.client.force_login(self.creator)
        resp = self.client.post(
            reverse("auth:delete_teammate", kwargs={"teammate_id": self.user1.id})
        )
        self.assertEqual(resp.status_code, 302)

    def test_delete_teammate(self):
        self.creator.team.teammates.add(self.user1)
        self.user1.team.teammates.add(self.creator)
        self.client.force_login(self.creator)
        resp = self.client.post(
            reverse("auth:delete_teammate", kwargs={"teammate_id": self.user1.id})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(self.creator, self.user1.team.teammates.all())


class TransferOwnershipTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser(
            username="foobar", email="foo@bar.com", password="barbaz"
        )
        self.user1 = base.UserFactory(
            username="User1", first_name="Old", last_name="User"
        )
        self.user2 = base.UserFactory(
            username="User2", first_name="New", last_name="User"
        )
        self.client.force_login(user=self.user)
        data = Data(name="Test")
        data.created_by = self.user1
        data.save()

    def test_transfer_ownership(self):
        users = {
            "old_user": self.user1.id,
            "new_user": self.user2.id,
            "disable_old_user": "yes",
        }
        response = self.client.post(reverse("auth:transfer_ownership"), users)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(id=self.user1.id).is_active, False)
        self.assertEqual(Data.objects.get(name="Test").created_by, self.user2)
