from django.core.urlresolvers import reverse

from insitu.tests import base


class RequirementTests(base.CreateCheckTestCase):
    fields = ['name', 'note']
    related_fields = ['dissemination', 'quality']
    required_fields = ['name', 'dissemination', 'quality']

    def setUp(self):
        super().setUp()
        dissemination = base.DisseminationFactory()
        quality = base.ComponentFactory()

        self._DATA = {
            'name': 'TEST requirement',
            'note': 'TEST note',
            'dissemination': dissemination.pk,
            'quality': quality.pk,
        }

    def test_list_requirement_json(self):
        base.RequirementFactory()
        resp = self.client.get(reverse('requirement:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_requirement_json_filter(self):
        base.RequirementFactory(name="Test requirement")
        base.RequirementFactory(name="Other requirement")
        resp = self.client.get(reverse('requirement:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_requirements(self):
        base.RequirementFactory()
        resp = self.client.get(reverse('requirement:list'))
        self.assertTemplateUsed(resp, 'requirement/list.html')
