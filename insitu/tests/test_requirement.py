from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base


class RequirementTests(base.CreateCheckTestCase):
    fields = ['name', 'note']
    related_fields = ['dissemination', 'quality']
    required_fields = ['name', 'dissemination', 'quality']
    related_entities_updated = ['uncertainty', 'frequency', 'timeliness',
                                'horizontal_resolution', 'vertical_resolution']
    related_entities_fields = ['threshold', 'breakthrough', 'goal']

    def setUp(self):
        super().setUp()
        dissemination = base.DisseminationFactory()
        quality = base.QualityFactory()

        self._DATA = {
            'name': 'TEST requirement',
            'note': 'TEST note',
            'dissemination': dissemination.pk,
            'quality': quality.pk,
        }

        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self._DATA["_".join([entity, field])] = '5'
                self.errors["_".join([entity, field])] = self.REQUIRED_ERROR

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

    def test_detail_requirement(self):
        requirement = base.RequirementFactory()
        resp = self.client.get(reverse('requirement:detail',
                                       kwargs={'pk': requirement.pk}))
        self.assertEqual(resp.context['requirement'], requirement)

    def test_create_requirement_fields_required(self):
        data = {}
        resp = self.client.post(reverse('requirement:add'), data)
        self.check_required_errors(resp, self.errors)

    def test_create_requirement(self):
        data = self._DATA
        resp = self.client.post(reverse('requirement:add'), data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Requirement, data)

    def test_edit_requirement(self):
        requirement = base.RequirementFactory()
        data = self._DATA
        resp = self.client.post(reverse('requirement:edit',
                                        kwargs={'pk': requirement.pk}), data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Requirement, data)
