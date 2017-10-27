import copy

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
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
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
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
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
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
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
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
        resp = self.client.post(
            reverse('requirement:product:delete',
                    kwargs={'requirement_pk': product_requirement.requirement.pk,
                            'pk': product_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.ProductRequirement)

    def test_product_group_requirement_add_required_fields(self):
        data = {}
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        errors_requirement = self.errors.copy()
        errors_requirement.pop('requirement')
        errors_requirement.pop('product')
        errors_requirement['product_group'] = ['This field is required.']

        resp = self.client.post(reverse('requirement:product:add_group',
                                        kwargs={
                                            'requirement_pk': requirement.pk}),
                                data)
        self.check_required_errors(resp, errors_requirement)

    def test_product_group_requirement_add(self):
        data = copy.deepcopy(self._DATA)
        data.pop('product')
        product_group = base.ProductGroupFactory()
        data['product_group'] = product_group.pk
        resp = self.client.post(
            reverse('requirement:product:add_group',
                    kwargs={'requirement_pk': self._DATA['requirement']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, self._DATA)


class ProductRequirementPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        super().setUp()
        self.login_url = reverse('auth:login')

    def test_product_requirement_add_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:add',
                        kwargs={'requirement_pk': requirement.pk}))

    def test_product_requirement_edit_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:edit',
                        kwargs={'requirement_pk': requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_delete_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:delete',
                        kwargs={'requirement_pk': requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_add_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:add',
                        kwargs={'requirement_pk': requirement.pk}))

    def test_product_requirement_edit_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:edit',
                        kwargs={'requirement_pk': requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_requirement_delete_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement,
            created_by=self.creator
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:delete',
                        kwargs={'requirement_pk': requirement.pk,
                                'pk': product_requirement.pk}))

    def test_product_group_requirement_add_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:product:add_group',
                        kwargs={'requirement_pk': requirement.pk}))

    def test_product_group_requirement_add_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('requirement:list'),
            url=reverse('requirement:product:add_group',
                        kwargs={'requirement_pk': requirement.pk}))
