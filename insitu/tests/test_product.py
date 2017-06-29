import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from insitu import models
from insitu.tests.base import create_product_group, create_status, create_coverage, create_component


class ProductTests(TestCase):
    def setUp(self):
        self._PRODUCT_DATA = {
            'acronym': 'TST',
            'name': 'TEST product',
            'note': 'TEST note',
            'description': 'TEST description',
            'group': create_product_group().pk,
            'component': create_component().pk,
            'status': create_status().pk,
            'coverage': create_coverage().pk
        }

    def test_create_product_fields_required(self):
        pass

    def test_create_product(self):
        data = self._PRODUCT_DATA
        resp = self.client.post(reverse('product:add'), data)
        self.assertEqual(resp.status_code, 302)
        qs = models.Product.objects.all()
        self.assertEqual(qs.count(), 1)
        product = qs.first()
        for attribute in ['acronym', 'name', 'note', 'description']:
            self.assertEqual(getattr(product, attribute), data[attribute])
        for related_object in ['group', 'component', 'status', 'coverage']:
            self.assertEqual(getattr(product, related_object).pk, data[related_object])
