from django.core.urlresolvers import reverse
from django.test import TestCase

from insitu import models
from insitu.tests import factories

REQUIRED_ERROR = ['This field is required.']


class ProductTests(TestCase):
    def setUp(self):
        self.fields = ['acronym', 'name', 'note', 'description']
        self.related_fields = ['group', 'component', 'status', 'coverage']
        self.required_fields = ['acronym', 'name', 'group', 'component',
                                'status', 'coverage']

        group = factories.ProductGroupFactory()
        component = factories.ComponentFactory()
        status = factories.ProductStatusFactory()
        coverage = factories.CoverageFactory()

        self._PRODUCT_DATA = {
            'acronym': 'TST',
            'name': 'TEST product',
            'note': 'TEST note',
            'description': 'TEST description',
            'group': group.pk,
            'component': component.pk,
            'status': status.pk,
            'coverage': coverage.pk
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

    def test_list_product(self):
        factories.ProductFactory()
        resp = self.client.get(reverse('product:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIs(data['recordsTotal'], 1)
        self.assertIs(data['recordsFiltered'], 1)

    def test_detail_product(self):
        product = factories.ProductFactory()
        resp = self.client.get(reverse('product:detail',
                               kwargs={'pk': product.pk}))
        self.assertEqual(resp.context['product'], product)

    def test_edit_product(self):
        product = factories.ProductFactory()
        data = self._PRODUCT_DATA
        resp = self.client.post(
            reverse('product:edit', kwargs={'pk': product.pk}),
            data)
        self.assertEqual(resp.status_code, 302)

        qs = models.Product.objects.all()
        self.assertEqual(qs.count(), 1)
        product = qs.first()
        for field in self.fields:
            self.assertEqual(getattr(product, field), data[field])
        for related_field in self.related_fields:
            self.assertEqual(getattr(product, related_field).pk, data[related_field])
