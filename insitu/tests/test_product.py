from django.core.urlresolvers import reverse
from django.test import TestCase

from insitu import models
from insitu.tests.base import create_product_group, create_status, create_coverage, create_component

REQUIRED_ERROR = ['This field is required.']


class ProductTests(TestCase):
    def setUp(self):
        self.fields = ['acronym', 'name', 'note', 'description']
        self.related_fields = ['group', 'component', 'status', 'coverage']
        self.required_fields = ['acronym', 'name', 'group', 'component',
                                'status', 'coverage']
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
        data = {}
        resp = self.client.post(reverse('product:add'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        errors = {field: REQUIRED_ERROR for field in self.required_fields}
        self.assertDictEqual(resp.context['form'].errors, errors)

    def test_create_product(self):
        data = self._PRODUCT_DATA
        resp = self.client.post(reverse('product:add'), data)
        self.assertEqual(resp.status_code, 302)
        qs = models.Product.objects.all()
        self.assertEqual(qs.count(), 1)
        product = qs.first()
        for field in self.fields:
            self.assertEqual(getattr(product, field), data[field])
        for related_field in self.related_fields:
            self.assertEqual(getattr(product, related_field).pk, data[related_field])
