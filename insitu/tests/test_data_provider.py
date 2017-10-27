from django.core.urlresolvers import reverse

from insitu import models
from insitu.documents import DataProviderDoc
from insitu.tests import base


class DataProviderTests(base.FormCheckTestCase):
    fields = ['name', 'is_network', 'description']
    many_to_many_fields = ['networks', 'countries']
    required_fields = ['name', 'is_network', 'countries']

    def setUp(self):
        super().setUp()
        countries = [
            base.CountryFactory(code="TST1"),
            base.CountryFactory(code="TST2")
        ]

        self._DATA = {
            'name': 'test name',
            'description': 'test description',
            'countries': [country.pk for country in countries],
            'is_network': True
        }

        self.details_fields = ['acronym', 'website', 'address', 'phone',
                               'email', 'contact_person', 'provider_type',
                               'data_provider']

        self.details_required_fields = ['provider_type']

        provider_type = base.ProviderTypeFactory()
        self._DETAILS_DATA = {
            'acronym': 'acronym',
            'website': 'test website',
            'address': 'test address',
            'phone': 'test phone',
            'email': 'test email',
            'contact_person': 'test person',
            'provider_type': provider_type.pk
        }
        user = base.UserFactory()
        self.client.force_login(user)

    def test_list_provider_json(self):
        base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse('provider:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_provider_json_filter(self):
        base.DataProviderFactory(name="Test provider",
                                 created_by=self.creator,
                                 countries=[base.CountryFactory(code='RO')])
        base.DataProviderFactory(name="Other provider",
                                 created_by=self.creator,
                                 countries=[base.CountryFactory(code='UK')])
        resp = self.client.get(reverse('provider:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_providers(self):
        base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse('provider:list'))
        self.assertTemplateUsed(resp, 'data_provider/list.html')

    def test_detail_provider(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse('provider:detail',
                                       kwargs={'pk': provider.pk}))
        self.assertEqual(resp.context['provider'], provider)

    def test_add_network_provider_required_fields(self):
        data = {}
        resp = self.client.post(reverse('provider:add_network'), data)
        self.check_required_errors(resp, self.errors)

    def test_get_add_network_provider(self):
        resp = self.client.get(reverse('provider:add_network'))
        self.assertEqual(resp.status_code, 200)

    def test_add_network_provider(self):
        data = self._DATA
        resp = self.client.post(reverse('provider:add_network'), data)
        self.assertEqual(resp.status_code, 302)
        data['networks'] = []
        self.check_single_object(models.DataProvider, data)

    def test_get_edit_network_provider(self):
        network = base.DataProviderFactory()
        resp = self.client.get(reverse('provider:edit_network',
                                       kwargs={'pk': network.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_network_provider(self):
        self.login_creator()
        data = self._DATA
        network = base.DataProviderFactory(is_network=True,
                                           created_by=self.creator)
        resp = self.client.post(reverse('provider:edit_network',
                                        kwargs={'pk': network.pk}),
                                data)
        self.assertEqual(resp.status_code, 302)
        data['networks'] = []
        self.check_single_object(models.DataProvider, data)

    def test_get_edit_network_members_provider(self):
        network = base.DataProviderFactory(is_network=True,
                                           created_by=self.creator)
        resp = self.client.get(reverse('provider:edit_network_members',
                                       kwargs={'pk': network.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_network_members_provider(self):
        self.login_creator()
        member_1 = base.DataProviderFactory(id=1,
                                            name='test member 1',
                                            is_network=True,
                                            created_by=self.creator,
                                            countries=[
                                                base.CountryFactory(code="T1").pk])
        member_2 = base.DataProviderFactory(id=2,
                                            name='test member 2',
                                            is_network=False,
                                            created_by=self.creator,
                                            countries=[
                                                base.CountryFactory(code="T2").pk])
        member_3 = base.DataProviderFactory(id=3,
                                            name='test member 3',
                                            is_network=True,
                                            created_by=self.creator,
                                            countries=[
                                                base.CountryFactory(code="T3").pk])
        network = base.DataProviderFactory(is_network=True,
                                           created_by=self.creator)
        data = dict()
        data['members'] = [member_1.pk, member_2.pk, member_3.pk]
        resp = self.client.post(reverse('provider:edit_network_members',
                                        kwargs={'pk': network.pk}),
                                data)

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 3)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)
        self.assertEqual(network.members.get(id=member_2.pk).name, member_2.name)
        self.assertEqual(network.members.get(id=member_3.pk).name, member_3.name)

    def test_edit_network_members_validation_provider(self):
        self.login_creator()
        network = base.DataProviderFactory(id=1,
                                           created_by=self.creator,
                                           is_network=True)
        data = dict()
        data['members'] = [1]
        resp = self.client.post(reverse('provider:edit_network_members',
                                        kwargs={'pk': network.pk}),
                                data)

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form'].errors['__all__'][0], 'Members should be different than the network.')

    def test_delete_network_members_provider(self):
        self.login_creator()
        member_1 = base.DataProviderFactory(id=1,
                                            name='test member 1',
                                            is_network=True,
                                            created_by=self.creator,
                                            countries=[
                                                base.CountryFactory(code="T1").pk])
        member_2 = base.DataProviderFactory(id=2,
                                            name='test member 2',
                                            is_network=False,
                                            created_by=self.creator,
                                            countries=[
                                                base.CountryFactory(code="T2").pk])
        network = base.DataProviderFactory(id=3,
                                           is_network=True,
                                           created_by=self.creator,
                                           members=[member_1.pk, member_2.pk])
        data = dict()
        data['members'] = [member_1.pk]
        resp = self.client.post(reverse('provider:edit_network_members',
                                        kwargs={'pk': network.pk}),
                                data)

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 1)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)

    def test_get_add_non_network_provider_required_fields(self):
        resp = self.client.get(reverse('provider:add_non_network'))
        self.assertEqual(resp.status_code, 200)

    def test_add_non_network_provider_required_fields(self):
        data = {}
        resp = self.client.post(reverse('provider:add_non_network'), data)
        non_network_fields = self.required_fields
        non_network_fields.remove('is_network')
        provider_errors = {field: self.REQUIRED_ERROR for field in non_network_fields}
        self.check_required_errors(resp, provider_errors)

        detail_errors = {field: self.REQUIRED_ERROR for field in
                         self.details_required_fields}
        self.assertDictEqual(resp.context['details'].errors, detail_errors)

    def test_add_non_network_provider(self):
        data = self._DATA
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        network_1 = base.DataProviderFactory(name='test network',
                                             is_network=True,
                                             created_by=self.creator,
                                             countries=[
                                                base.CountryFactory(code="T1").pk])
        network_2 = base.DataProviderFactory(name='test network 2',
                                             is_network=True,
                                             created_by=self.creator,
                                             countries=[
                                                base.CountryFactory(code="T2").pk])
        data['networks'] = [network_1.pk, network_2.pk]
        resp = self.client.post(reverse('provider:add_non_network'), data)

        provider = models.DataProvider.objects.last()
        details = provider.details.first()
        network_1.refresh_from_db()
        network_2.refresh_from_db()
        data['is_network'] = False

        self.assertEqual(resp.status_code, 302)
        self.check_object(provider, data)

        self.assertEqual(network_1.members.count(), 1)
        self.assertEqual(network_1.members.first(), provider)

        self.assertEqual(network_2.members.count(), 1)
        self.assertEqual(network_2.members.first(), provider)

        self.assertEqual(provider.networks.count(), 2)
        self.assertIn(network_1, provider.networks.all())
        self.assertIn(network_2, provider.networks.all())

        self.assertEqual(provider.details.count(), 1)
        details_data.pop('provider_type')
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, 'provider_type').pk,
                         data['provider_type'])

    def test_get_edit_non_network_provider(self):
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.get(reverse('provider:edit_non_network',
                                       kwargs={'pk': provider.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_non_network_provider(self):
        self.login_creator()
        data = self._DATA
        data['is_network'] = False
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        details = base.DataProviderDetailsFactory(data_provider=provider,
                                                  created_by=self.creator)
        resp = self.client.post(reverse('provider:edit_non_network',
                                        kwargs={'pk': provider.pk}),
                                data)

        self.assertEqual(resp.status_code, 302)
        provider.refresh_from_db()
        data['networks'] = []
        self.check_object(provider, data)
        details.refresh_from_db()
        details_data.pop('provider_type')
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, 'provider_type').pk,
                         data['provider_type'])

    def test_get_edit_network_provider(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=True,
                                            created_by=self.creator)
        resp = self.client.get(
            reverse('provider:edit_network',
                    kwargs={'pk': provider.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_edit_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.get(
            reverse('provider:edit_non_network',
                    kwargs={'pk': provider.pk}))

    def test_get_delete_data_provider_network(self):
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.get(reverse('provider:delete_network',
                                       kwargs={'pk': provider.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_data_provider_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.post(
            reverse('provider:delete_network',
                    kwargs={'pk': provider.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProvider)
        self.check_objects_are_soft_deleted(models.DataProvider,
                                            DataProviderDoc)

    def test_delete_data_provider_network_related_objects(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=True,
                                            created_by=self.creator)
        data = base.DataFactory(created_by=self.creator)
        base.DataProviderDetailsFactory(data_provider=provider,
                                        created_by=self.creator)
        base.DataProviderRelationFactory(provider=provider,
                                         data=data,
                                         created_by=self.creator)
        self.client.post(
            reverse('provider:delete_network',
                    kwargs={'pk': provider.pk})
        )
        self.check_objects_are_soft_deleted(models.DataProviderDetails)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)

    def test_get_delete_data_provider_non_network(self):
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.get(reverse('provider:delete_non_network',
                                       kwargs={'pk': provider.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_data_provider_non_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        resp = self.client.post(
            reverse('provider:delete_non_network',
                    kwargs={'pk': provider.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProvider)
        self.check_objects_are_soft_deleted(models.DataProvider,
                                            DataProviderDoc)

    def test_delete_data_provider_non_network_related_objects(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False,
                                            created_by=self.creator)
        data = base.DataFactory(created_by=self.creator)
        base.DataProviderDetailsFactory(data_provider=provider,
                                        created_by=self.creator)
        base.DataProviderRelationFactory(provider=provider,
                                         data=data,
                                         created_by=self.creator)
        self.client.post(
            reverse('provider:delete_non_network',
                    kwargs={'pk': provider.pk})
        )
        self.check_objects_are_soft_deleted(models.DataProviderDetails)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)


class DataProviderPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.redirect_provider_url = reverse('provider:list')
        self.redirect_login_url = reverse('auth:login')

    def test_list_provider_json_non_auth(self):
        self.check_permission_denied(method='GET',
                                     url=reverse('provider:json'))

    def test_list_providers_non_auth(self):
        self.check_user_redirect(method='GET',
                                 url=reverse('provider:list'),
                                 redirect_url=self.redirect_login_url)

    def test_detail_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect(method='GET',
                                 url=reverse('provider:detail',
                                             kwargs={'pk': provider.pk}),
                                 redirect_url=self.redirect_login_url)

    def test_add_network_provider_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('provider:add_network'),
            redirect_url=self.redirect_login_url)

    def test_edit_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('provider:edit_network',
                        kwargs={'pk': provider.pk}),
            redirect_url=self.redirect_login_url)

    def test_delete_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('provider:delete_network',
                        kwargs={'pk': provider.pk}),
            redirect_url=self.redirect_login_url)

    def test_add_non_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('provider:edit_network',
                        kwargs={'pk': provider.pk}),
            redirect_url=self.redirect_login_url)

    def test_edit_non_network_provider_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('provider:add_non_network'),
            redirect_url=self.redirect_login_url)

    def test_delete_non_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('provider:delete_non_network',
                        kwargs={'pk': provider.pk}),
            redirect_url=self.redirect_login_url)
