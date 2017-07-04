from django.core.urlresolvers import reverse

from insitu.tests import base


class DataResponsibleTests(base.CreateCheckTestCase):

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
