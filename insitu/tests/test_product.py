from django.core.urlresolvers import reverse

from insitu import models
from insitu.documents import ProductDoc
from insitu.tests import base
from insitu.utils import ALL_OPTIONS_LABEL


class ProductTests(base.FormCheckTestCase):
    fields = ['acronym', 'name', 'note', 'description']
    related_fields = ['group', 'component', 'status', 'coverage']
    required_fields = ['acronym', 'name', 'group', 'component',
                       'status', 'coverage']

    def setUp(self):
        super().setUp()
        group = base.ProductGroupFactory()
        component = base.ComponentFactory()
        status = base.ProductStatusFactory()
        coverage = base.CoverageFactory()

        responsible_user = base.UserFactory()
        base.CopernicususResponsibleFactory(user=responsible_user)
        self.client.force_login(responsible_user)
        self._DATA = {
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
        self.check_required_errors(resp, self.errors)

    def test_create_product(self):
        data = self._DATA
        resp = self.client.post(reverse('product:add'), data)
        self.assertEqual(resp.status_code, 302)

        self.check_single_object(models.Product, data)

    def test_list_product_json(self):
        base.ProductFactory()
        resp = self.client.get(reverse('product:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_product_json_filter(self):
        base.ProductFactory(name="Test product")
        base.ProductFactory(name="Other product")
        resp = self.client.get(reverse('product:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_products(self):
        base.ProductFactory()
        resp = self.client.get(reverse('product:list'))
        self.assertTemplateUsed(resp, 'product/list.html')

    def test_detail_product(self):
        product = base.ProductFactory()
        resp = self.client.get(reverse('product:detail',
                                       kwargs={'pk': product.pk}))
        self.assertEqual(resp.context['product'], product)

    def test_edit_product(self):
        product = base.ProductFactory()
        data = self._DATA
        resp = self.client.post(
            reverse('product:edit', kwargs={'pk': product.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Product, data)

    def test_product_component_filter_service(self):
        service_1 = base.CopernicusServiceFactory(name="Special service")
        service_2 = base.CopernicusServiceFactory(name="Other service")
        base.ComponentFactory(service=service_1)
        base.ComponentFactory(service=service_2)

        resp = self.client.get(reverse('product:filter_components'),
                               {'service': service_1.name})
        data = resp.json()
        self.assertEqual(len(data['components']), 2)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])

        resp = self.client.get(reverse('product:filter_components'),
                               {'service': 'No such name'})
        data = resp.json()
        self.assertEqual(len(data['components']), 1)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])

    def test_product_component_filter_entity(self):
        entity_1 = base.EntrustedEntityFactory(acronym="Special")
        entity_2 = base.EntrustedEntityFactory(acronym="Other")
        base.ComponentFactory(entrusted_entity=entity_1)
        base.ComponentFactory(entrusted_entity=entity_2)

        resp = self.client.get(reverse('product:filter_components'),
                               {'entity': entity_1.acronym})
        data = resp.json()
        self.assertEqual(len(data['components']), 2)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])

        resp = self.client.get(reverse('product:filter_components'),
                               {'entity': 'No such name'})
        data = resp.json()
        self.assertEqual(len(data['components']), 1)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])

    def test_product_component_filter_entity_and_service(self):
        service_1 = base.CopernicusServiceFactory(name="Special service")
        service_2 = base.CopernicusServiceFactory(name="Other service")
        entity_1 = base.EntrustedEntityFactory(acronym="Special")
        entity_2 = base.EntrustedEntityFactory(acronym="Other")

        base.ComponentFactory(service=service_1,
                              entrusted_entity=entity_1)
        base.ComponentFactory(service=service_1,
                              entrusted_entity=entity_2)
        base.ComponentFactory(service=service_2,
                              entrusted_entity=entity_1)

        resp = self.client.get(reverse('product:filter_components'),
                               {'service': service_1.name,
                                'entity': entity_1.acronym})
        data = resp.json()
        self.assertEqual(len(data['components']), 2)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])

        resp = self.client.get(reverse('product:filter_components'),
                               {'service': 'No such name',
                                'entity': 'No such'})
        data = resp.json()
        self.assertEqual(len(data['components']), 1)
        self.assertTrue(ALL_OPTIONS_LABEL in data['components'])


    def test_delete_product(self):
        product = base.ProductFactory()
        resp = self.client.post(
            reverse('product:delete', kwargs={'pk': product.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.Product)
        self.check_objects_are_soft_deleted(models.Product, ProductDoc)


    def test_delete_product_related_objects(self):
        product = base.ProductFactory()
        base.ProductRequirementFactory(product=product)
        self.client.post(
            reverse('product:delete', kwargs={'pk': product.pk})
        )
        self.check_objects_are_soft_deleted(models.ProductRequirement)


class ProductPermissionTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.redirect_product_url_non_auth = reverse('auth:login')
        self.redirect_product_url_auth = reverse('product:list')
        self.methods = ['GET', 'POST']

    def test_product_ad_not_auth(self):
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_non_auth,
            url=reverse('product:add'))

    def test_product_edit_not_auth(self):
        product = base.ProductFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_non_auth,
            url=reverse('product:edit', kwargs={'pk': product.pk}))

    def test_product_delete_not_auth(self):
        product = base.ProductFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_non_auth,
            url=reverse('product:delete', kwargs={'pk': product.pk}))

    def test_product_relation_add_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_auth,
            url=reverse('product:add'))

    def test_product_relation_edit_auth(self):
        product = base.ProductFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_auth,
            url=reverse('product:edit', kwargs={'pk': product.pk}))

    def test_product_relation_delete_auth(self):
        product = base.ProductFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_product_url_auth,
            url=reverse('product:delete', kwargs={'pk': product.pk}))
