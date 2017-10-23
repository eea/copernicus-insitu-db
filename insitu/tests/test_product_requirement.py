from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class ProductRequirementTests(base.FormCheckTestCase):
    fields = ['note']
    related_fields = ['requirement', 'product', 'level_of_definition', 
                      'relevance', 'criticality']
    many_to_many_fields = ['barriers']
    required_fields = ['requirement', 'product', 'level_of_definition',
                       'relevance', 'criticality', 'barriers']

    def setUp(self):
        super().setUp()
        requirement = base.RequirementFactory()
        product = base.ProductFactory()
        level_of_definition = base.DefinitionLevelFactory()
        relevance = base.RelevanceFactory()
        criticality = base.CriticalityFactory()
        barriers = [base.BarrierFactory(), base.BarrierFactory()]

        self._DATA = {
            'note': 'test note',
            'requirement': requirement.pk,
            'product': product.pk,
            'level_of_definition': level_of_definition.pk,
            'relevance': relevance.pk,
            'criticality': criticality.pk,
            'barriers': [barrier.pk for barrier in barriers]
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususProviderFactory(user=user)

    def test_product_requirement_add_required_fields(self):
        data = {}
        requirement = base.RequirementFactory()
        errors_requirement = self.errors.copy()
        errors_requirement.pop('requirement')

        resp = self.client.post(reverse('requirement:product:add',
                                        kwargs={'requirement_pk': requirement.pk}),
                                data)
        self.check_required_errors(resp, errors_requirement)

    def test_product_requirement_add(self):
        data = self._DATA
        resp = self.client.post(
            reverse('requirement:product:add',
                    kwargs={'requirement_pk': self._DATA['requirement']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_edit(self):
        product_requirement = base.ProductRequirementFactory()
        data = self._DATA
        data.pop('product')
        data.pop('requirement')
        resp = self.client.post(
            reverse('requirement:product:edit',
                    kwargs={'requirement_pk': product_requirement.requirement.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['product'] = product_requirement.product.pk
        data['requirement'] = product_requirement.requirement.pk
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_delete(self):
        data = {}
        product_requirement = base.ProductRequirementFactory()
        resp = self.client.post(
            reverse('requirement:product:delete',
                    kwargs={'requirement_pk': product_requirement.requirement.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.ProductRequirement)


class ProductRequirementPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.login_url = reverse('auth:login')

    def test_product_requirement_add_not_auth(self):
        data_requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_product_requirement_edit_not_auth(self):
        data_requirement = base.RequirementFactory()
        product_requirement = base.ProductRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_delete_not_auth(self):
        data_requirement = base.RequirementFactory()
        product_requirement = base.ProductRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_add_auth(self):
        data_requirement = base.RequirementFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_product_requirement_edit_auth(self):
        data_requirement = base.RequirementFactory()
        product_requirement = base.ProductRequirementFactory(
            requirement=data_requirement)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_delete_auth(self):
        data_requirement = base.RequirementFactory()
        product_requirement = base.ProductRequirementFactory(
            requirement=data_requirement)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': product_requirement.pk}))
