from django.core.urlresolvers import reverse

from insitu import models
from insitu.documents import DataResponsibleDoc
from insitu.tests import base


class DataResponsibleTests(base.FormCheckTestCase):
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

        self.details_fields = ['acronym', 'website', 'address', 'phone', 'email',
                               'contact_person', 'responsible_type', 'data_responsible']

        self.details_required_fields = ['acronym', 'website', 'address', 'phone',
                                        'email', 'contact_person', 'responsible_type']

        responsible_type = base.ResponsibleTypeFactory()
        self._DETAILS_DATA = {
            'acronym': 'acronym',
            'website': 'test website',
            'address': 'test address',
            'phone': 'test phone',
            'email': 'test email',
            'contact_person': 'test person',
            'responsible_type': responsible_type.pk
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususResponsibleFactory(user=user)

    def test_list_responsible_json(self):
        base.DataResponsibleFactory()
        resp = self.client.get(reverse('responsible:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_responsible_json_filter(self):
        base.DataResponsibleFactory(name="Test responsible",
                                    countries=[base.CountryFactory(code='RO')])
        base.DataResponsibleFactory(name="Other responsible",
                                    countries=[base.CountryFactory(code='UK')])
        resp = self.client.get(reverse('responsible:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_responsibles(self):
        base.DataResponsibleFactory()
        resp = self.client.get(reverse('responsible:list'))
        self.assertTemplateUsed(resp, 'data_responsible/list.html')

    def test_detail_responsible(self):
        responsible = base.DataResponsibleFactory()
        resp = self.client.get(reverse('responsible:detail',
                                       kwargs={'pk': responsible.pk}))
        self.assertEqual(resp.context['responsible'], responsible)

    def test_add_network_responsible_required_fields(self):
        data = {}
        resp = self.client.post(reverse('responsible:add_network'), data)
        self.check_required_errors(resp, self.errors)

    def test_add_network_responsible(self):
        data = self._DATA
        resp = self.client.post(reverse('responsible:add_network'), data)
        self.assertEqual(resp.status_code, 302)
        data['networks'] = []
        self.check_single_object(models.DataResponsible, data)

    def test_edit_network_responsible(self):
        data = self._DATA
        network = base.DataResponsibleFactory(is_network=True)
        resp = self.client.post(reverse('responsible:edit_network',
                                       kwargs={'pk': network.pk}),
                                data)
        self.assertEqual(resp.status_code, 302)
        data['networks'] = []
        self.check_single_object(models.DataResponsible, data)

    def test_edit_network_members_responsible(self):
        member_1 = base.DataResponsibleFactory(id=1,
                                               name='test member 1',
                                               is_network=True,
                                               countries=[
                                                    base.CountryFactory(code="T1").pk])
        member_2 = base.DataResponsibleFactory(id=2,
                                               name='test member 2',
                                               is_network=False,
                                               countries=[
                                                    base.CountryFactory(code="T2").pk])
        member_3 = base.DataResponsibleFactory(id=3,
                                               name='test member 3',
                                               is_network=True,
                                               countries=[
                                                    base.CountryFactory(code="T3").pk])
        network = base.DataResponsibleFactory(is_network=True)
        data = dict()
        data['members'] = [member_1.pk, member_2.pk, member_3.pk]
        resp = self.client.post(reverse('responsible:edit_network_members',
                                        kwargs={'pk': network.pk}),
                                data)

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 3)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)
        self.assertEqual(network.members.get(id=member_2.pk).name, member_2.name)
        self.assertEqual(network.members.get(id=member_3.pk).name, member_3.name)

    def test_delete_network_members_responsible(self):
        member_1 = base.DataResponsibleFactory(id=1,
                                               name='test member 1',
                                               is_network=True,
                                               countries=[
                                                   base.CountryFactory(code="T1").pk])
        member_2 = base.DataResponsibleFactory(id=2,
                                               name='test member 2',
                                               is_network=False,
                                               countries=[
                                                   base.CountryFactory(code="T2").pk])
        network = base.DataResponsibleFactory(id=3,
                                              is_network=True,
                                              members=[member_1.pk, member_2.pk])
        data = dict()
        data['members'] = [member_1.pk]
        resp = self.client.post(reverse('responsible:edit_network_members',
                                        kwargs={'pk': network.pk}),
                                data)

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 1)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)

    def test_add_non_network_responsible_required_fields(self):
        data = {}
        resp = self.client.post(reverse('responsible:add_non_network'), data)
        non_network_fields = self.required_fields
        non_network_fields.remove('is_network')
        responsible_errors = {field: self.REQUIRED_ERROR for field in non_network_fields}
        self.check_required_errors(resp, responsible_errors)

        detail_errors = {field: self.REQUIRED_ERROR for field in
                         self.details_required_fields}
        self.assertDictEqual(resp.context['details'].errors, detail_errors)

    def test_add_non_network_responsible(self):
        data = self._DATA
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        network_1 = base.DataResponsibleFactory(name='test network',
                                                is_network=True,
                                                countries=[
                                                    base.CountryFactory(code="T1").pk])
        network_2 = base.DataResponsibleFactory(name='test network 2',
                                                is_network=True,
                                                countries=[
                                                    base.CountryFactory(code="T2").pk])
        data['networks'] = [network_1.pk, network_2.pk]
        resp = self.client.post(reverse('responsible:add_non_network'), data)

        responsible = models.DataResponsible.objects.last()
        details = responsible.details.first()
        network_1.refresh_from_db()
        network_2.refresh_from_db()
        data['is_network'] = False

        self.assertEqual(resp.status_code, 302)
        self.check_object(responsible, data)

        self.assertEqual(network_1.members.count(), 1)
        self.assertEqual(network_1.members.first(), responsible)

        self.assertEqual(network_2.members.count(), 1)
        self.assertEqual(network_2.members.first(), responsible)

        self.assertEqual(responsible.networks.count(), 2)
        self.assertIn(network_1, responsible.networks.all())
        self.assertIn(network_2, responsible.networks.all())

        self.assertEqual(responsible.details.count(), 1)
        details_data.pop('responsible_type')
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, 'responsible_type').pk,
                         data['responsible_type'])

    def test_edit_non_network_responsible(self):
        data = self._DATA
        data['is_network'] = False
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        responsible = base.DataResponsibleFactory(is_network=False)
        details = base.DataResponsibleDetailsFactory(data_responsible=responsible
                                                     )
        resp = self.client.post(reverse('responsible:edit_non_network',
                                        kwargs={'pk': responsible.pk}),
                                data)

        self.assertEqual(resp.status_code, 302)
        responsible.refresh_from_db()
        data['networks'] = []
        self.check_object(responsible, data)
        details.refresh_from_db()
        details_data.pop('responsible_type')
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, 'responsible_type').pk,
                         data['responsible_type'])

    def test_delete_data_responsible_network(self):
        responsible = base.DataResponsibleFactory(is_network=False)
        resp = self.client.post(
            reverse('responsible:delete_network',
                    kwargs={'pk': responsible.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataResponsible)
        self.check_objects_are_soft_deleted(models.DataResponsible,
                                            DataResponsibleDoc)

    def test_delete_data_responsible_network_related_objects(self):
        responsible = base.DataResponsibleFactory(is_network=True)
        base.DataResponsibleDetailsFactory(data_responsible=responsible)
        base.DataResponsibleRelationFactory(responsible=responsible)
        self.client.post(
            reverse('responsible:delete_network',
                    kwargs={'pk': responsible.pk})
        )
        self.check_objects_are_soft_deleted(models.DataResponsibleDetails)
        self.check_objects_are_soft_deleted(models.DataResponsibleRelation)

    def test_delete_data_responsible_non_network(self):
        responsible = base.DataResponsibleFactory(is_network=False)
        resp = self.client.post(
            reverse('responsible:delete_non_network',
                    kwargs={'pk': responsible.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataResponsible)
        self.check_objects_are_soft_deleted(models.DataResponsible,
                                            DataResponsibleDoc)

    def test_delete_data_responsible_non_network_related_objects(self):
        responsible = base.DataResponsibleFactory(is_network=False)
        base.DataResponsibleDetailsFactory(data_responsible=responsible)
        base.DataResponsibleRelationFactory(responsible=responsible)
        self.client.post(
            reverse('responsible:delete_non_network',
                    kwargs={'pk': responsible.pk})
        )
        self.check_objects_are_soft_deleted(models.DataResponsibleDetails)
        self.check_objects_are_soft_deleted(models.DataResponsibleRelation)


class DataResponsiblePermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        self.redirect_responsible_url = reverse('responsible:list')
        self.redirect_login_url = reverse('auth:login')

    def test_list_responsible_json_non_auth(self):
        self.check_permission_denied(method='GET',
                                     url=reverse('responsible:json'))

    def test_list_responsibles_non_auth(self):
        self.check_user_redirect(method='GET',
                                 url=reverse('responsible:list'),
                                 redirect_url=self.redirect_login_url)

    def test_detail_responsible_non_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_user_redirect(method='GET',
                                 url=reverse('responsible:detail',
                                             kwargs={'pk': responsible.pk}),
                                 redirect_url=self.redirect_login_url)

    def test_add_network_responsible_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('responsible:add_network'),
            redirect_url=self.redirect_login_url)

    def test_edit_network_responsible_non_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            url=reverse('responsible:edit_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_login_url)

    def test_delete_network_responsible_non_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            url=reverse('responsible:delete_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_login_url)

    def test_add_non_network_responsible_non_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            url=reverse('responsible:edit_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_login_url)

    def test_edit_non_network_responsible_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('responsible:add_non_network'),
            redirect_url=self.redirect_login_url)

    def test_delete_non_network_responsible_non_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            url=reverse('responsible:delete_non_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_login_url)

    def test_add_network_responsible_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:add_network'),
            redirect_url=self.redirect_responsible_url)

    def test_edit_network_responsible_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:edit_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_responsible_url)

    def test_delete_network_responsible_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:delete_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_responsible_url)

    def test_add_non_network_responsible_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:add_non_network'),
            redirect_url=self.redirect_responsible_url)

    def test_edit_non_network_responsible_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:edit_non_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_responsible_url)

    def test_delete_non_network_responsible_auth(self):
        responsible = base.DataResponsibleFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('responsible:delete_non_network',
                        kwargs={'pk': responsible.pk}),
            redirect_url=self.redirect_responsible_url)
