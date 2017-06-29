import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from insitu import models
from insitu.tests.base import create_product_group

_PRODUCT_DATA = {
    'acronym': 'TST',
    'name': 'TEST product',
    'description': 'TEST description',
    'group': create_product_group('Test group'),
    'component': None,
    'status': None,
    'coverage': None,
    'note': 'TEST note'
}


class ProductTests(TestCase):

    def test_create_product(self):
        data = _PRODUCT_DATA
        resp = self.client.post(reverse('product:create'),
                                data=json.dumps(data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data)

        qs = models.Product.objects.all()
        self.assertEqual(qs.count(), 1)
        product = qs.first()
        self.assertEqual(product.name, data['name'])