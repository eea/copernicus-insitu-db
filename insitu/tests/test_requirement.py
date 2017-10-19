from django.core.urlresolvers import reverse

from insitu import models
from insitu.documents import RequirementDoc
from insitu.tests import base


class RequirementTests(base.FormCheckTestCase):
    fields = ['name', 'note']
    related_fields = ['dissemination', 'quality_control_procedure']
    required_fields = ['name', 'dissemination', 'quality_control_procedure',
                       'group']
    related_entities_updated = ['uncertainty', 'update_frequency', 'timeliness',
                                'horizontal_resolution', 'vertical_resolution']
    related_entities_fields = ['threshold', 'breakthrough', 'goal']

    def setUp(self):
        super().setUp()
        dissemination = base.DisseminationFactory()
        quality_control_procedure = base.QualityControlProcedureFactory()
        group = base.RequirementGroupFactory()
        responsible_user = base.UserFactory()
        base.CopernicususResponsibleFactory(user=responsible_user)
        self.client.force_login(responsible_user)

        self._DATA = {
            'name': 'TEST requirement',
            'note': 'TEST note',
            'dissemination': dissemination.pk,
            'quality_control_procedure': quality_control_procedure.pk,
            'group': group.pk,
        }

        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self._DATA["_".join([entity, field])] = ''
        self._DATA['uncertainty_goal'] = '1'
        self.errors['__all__'] = ['At least one metric is required.']

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

    def test_delete_requirement(self):
        requirement = base.RequirementFactory()
        resp = self.client.post(
            reverse('requirement:delete', kwargs={'pk': requirement.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.Requirement)
        self.check_objects_are_soft_deleted(models.Requirement, RequirementDoc)


    def test_delete_requirement_related_objects(self):
        requirement = base.RequirementFactory()
        base.ProductRequirementFactory(requirement=requirement)
        base.DataRequirementFactory(requirement=requirement)
        self.client.post(
            reverse('requirement:delete', kwargs={'pk': requirement.pk})
        )
        self.check_objects_are_soft_deleted(models.ProductRequirement)
        self.check_objects_are_soft_deleted(models.DataRequirement)


class RequirementPermissionTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.redirect_requirement_url_non_auth = reverse('auth:login')
        self.redirect_requirement_url_auth = reverse('requirement:list')
        self.methods = ['GET', 'POST']

    def test_list_requirement_json_non_auth(self):
        self.check_permission_denied(method='GET',
                                     url=reverse('requirement:json'))

    def test_requirement_list_not_auth(self):
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_non_auth,
            url=reverse('requirement:list'))

    def test_requirement_detail_not_auth(self):
        requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_non_auth,
            url=reverse('requirement:detail', kwargs={'pk': requirement.pk}))

    def test_requirement_add_not_auth(self):
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_non_auth,
            url=reverse('requirement:add'))

    def test_requirement_edit_not_auth(self):
        requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_non_auth,
            url=reverse('requirement:edit', kwargs={'pk': requirement.pk}))

    def test_requirement_delete_not_auth(self):
        requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_non_auth,
            url=reverse('requirement:delete', kwargs={'pk': requirement.pk}))

    def test_requirement_relation_add_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_auth,
            url=reverse('requirement:add'))

    def test_requirement_relation_edit_auth(self):
        requirement = base.RequirementFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_auth,
            url=reverse('requirement:edit', kwargs={'pk': requirement.pk}))

    def test_requirement_relation_delete_auth(self):
        requirement = base.RequirementFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_requirement_url_auth,
            url=reverse('requirement:delete', kwargs={'pk': requirement.pk}))
