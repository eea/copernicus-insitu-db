# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from insitu.tests import base
from django.test import TestCase
from django.urls import reverse


class ManagementTestCase(TestCase):

    def setUp(self):
        user = base.UserFactory(username='User Management', is_superuser=True)
        self.client.force_login(user)

    def test_export(self):
        url = reverse('pick:export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
