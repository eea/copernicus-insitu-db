from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base


class DataResponsibleTests(base.CreateCheckTestCase):
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

        self._DETAILS_DATA = {
            'acronym': 'acronym',
            'website': 'test website',
            'address': 'test address',
            'phone': 'test phone',
            'email': 'test email',
            'contact_person': 'test person',
            'responsible_type': 1
        }

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
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])

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
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])

