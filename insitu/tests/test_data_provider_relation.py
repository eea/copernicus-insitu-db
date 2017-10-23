from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class DataProviderRelationTests(base.FormCheckTestCase):
    fields = ['role']
    related_fields = ['data', 'provider']
    required_fields = ['role', 'data', 'provider']

    def setUp(self):
        super().setUp()
        data = base.DataFactory()
        countries = [base.CountryFactory(code='T1'),
                     base.CountryFactory(code='T2')]
        provider = base.DataProviderFactory(countries=countries)

        self._DATA = {
            'role': 1,
            'data': data.pk,
            'provider': provider.pk
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususProviderFactory(user=user)

    def test_provider_relation_add_required_fields(self):
        data = {}
        data_factory = base.DataFactory()
        errors_data = self.errors.copy()
        errors_data.pop('data')
        resp = self.client.post(reverse('data:provider:add',
                                        kwargs={'group_pk': data_factory.pk}),
                                data)
        self.check_required_errors(resp, errors_data)

    def test_provider_relation_add(self):
        data = self._DATA
        resp = self.client.post(reverse('data:provider:add',
                                        kwargs={'group_pk': self._DATA['data']}),
                                data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataProviderRelation, data)

    def test_provider_relation_edit(self):
        provider_relation = base.DataProviderRelationFactory()
        data = self._DATA
        data.pop('data')
        data.pop('provider')
        resp = self.client.post(
            reverse('data:provider:edit',
                    kwargs={'group_pk': provider_relation.data.pk,
                            'pk': provider_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data'] = provider_relation.data.pk
        data['provider'] = provider_relation.provider.pk
        self.check_single_object(models.DataProviderRelation, data)

    def test_provider_relation_delete(self):
        data = {}
        provider_relation = base.DataProviderRelationFactory()
        resp = self.client.post(
            reverse('data:provider:delete',
                    kwargs={'group_pk': provider_relation.data.pk,
                            'pk': provider_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProviderRelation)


class DataProviderRelationPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        self.login_url = reverse('auth:login')

    def test_provider_relation_add_not_auth(self):
        data = base.DataFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:provider:add',
                        kwargs={'group_pk': data.pk}))

    def test_provider_relation_delete_not_auth(self):
        data = base.DataFactory()
        provider_relation = base.DataProviderRelationFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:provider:delete',
                        kwargs={'group_pk': data.pk,
                                'pk': provider_relation.pk}))

    def test_provider_relation_edit_not_auth(self):
        data = base.DataFactory()
        provider_relation = base.DataProviderRelationFactory(data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:provider:edit',
                        kwargs={'group_pk': data.pk,
                                'pk': provider_relation.pk}))

    def test_provider_relation_add_auth(self):
        data = base.DataFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('data:list'),
            url=reverse('data:provider:add',
                        kwargs={'group_pk': data.pk}))

    def test_provider_relation_delete_auth(self):
        data = base.DataFactory()
        provider_relation = base.DataProviderRelationFactory(
            data=data)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('data:list'),
            url=reverse('data:provider:delete',
                        kwargs={'group_pk': data.pk,
                                'pk': provider_relation.pk}))

    def test_provider_relation_edit_auth(self):
        data = base.DataFactory()
        provider_relation = base.DataProviderRelationFactory(
            data=data)
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse('data:list'),
            url=reverse('data:provider:edit',
                        kwargs={'group_pk': data.pk,
                                'pk': provider_relation.pk}))
