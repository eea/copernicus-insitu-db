from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class DataRequirementTests(base.FormCheckTestCase):
    fields = ['note', 'information_costs', 'handling_costs']
    related_fields = ['data_group', 'requirement', 'level_of_compliance']
    required_fields = ['data_group', 'requirement', 'level_of_compliance']

    def setUp(self):
        super().setUp()
        data_group = base.DataGroupFactory()
        requirement = base.RequirementFactory()
        level_of_compliance = base.ComplianceLevelFactory()

        self._DATA = {
            'data_group': data_group.pk,
            'requirement': requirement.pk,
            'level_of_compliance': level_of_compliance.pk,
            'note': 'TEST note',
            'information_costs': True,
            'handling_costs': True
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususResponsibleFactory(user=user)

    def test_data_requirement_add_required_fields_from_data_group(self):
        data = {}
        data_group = base.DataGroupFactory()
        errors_data_group = self.errors.copy()
        errors_data_group.pop('data_group')
        resp = self.client.post(
            reverse('data_group:requirement:add',
                    kwargs={'data_group_pk': data_group.pk}),
            data)
        self.check_required_errors(resp, errors_data_group)

    def test_data_requirement_add_required_fields_from_requirement(self):
        data = {}
        requirement = base.RequirementFactory()
        errors_requirement = self.errors.copy()
        errors_requirement.pop('requirement')

        resp = self.client.post(
            reverse('requirement:data_group:add',
                    kwargs={'requirement_pk': requirement.pk}),
            data)
        self.check_required_errors(resp, errors_requirement)

    def test_data_requirement_add_from_data_group(self):
        data = self._DATA
        resp = self.client.post(
            reverse('data_group:requirement:add',
                    kwargs={'data_group_pk': self._DATA['data_group']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_add_from_requirement(self):
        data = self._DATA
        resp = self.client.post(
            reverse('requirement:data_group:add',
                    kwargs={'requirement_pk': self._DATA['requirement']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_edit_from_data_group(self):
        data_requirement = base.DataRequirementFactory()
        data = self._DATA
        data.pop('data_group')
        data.pop('requirement')
        resp = self.client.post(
            reverse('data_group:requirement:edit',
                    kwargs={'data_group_pk': data_requirement.data_group.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data_group'] = data_requirement.data_group.pk
        data['requirement'] = data_requirement.requirement.pk
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_edit_from_requirement(self):
        data_requirement = base.DataRequirementFactory()
        data = self._DATA
        data.pop('data_group')
        data.pop('requirement')
        resp = self.client.post(
            reverse('requirement:data_group:edit',
                    kwargs={'requirement_pk': data_requirement.requirement.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data_group'] = data_requirement.data_group.pk
        data['requirement'] = data_requirement.requirement.pk
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_delete_from_data_group(self):
        data = {}
        data_requirement = base.DataRequirementFactory()
        resp = self.client.post(
            reverse('data_group:requirement:delete',
                    kwargs={'data_group_pk': data_requirement.data_group.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataRequirement)

    def test_data_requirement_delete_from_requirement(self):
        data = {}
        data_requirement = base.DataRequirementFactory()
        resp = self.client.post(
            reverse('requirement:data_group:delete',
                    kwargs={'requirement_pk': data_requirement.requirement.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataRequirement)


class DataGroupRequirementPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.login_url = reverse('auth:login')

    def test_data_requirement_add_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:add',
                        kwargs={'data_group_pk': data_group.pk}))

    def test_data_requirement_delete_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        data_requirement = base.DataRequirementFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:edit',
                        kwargs={'data_group_pk': data_group.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_edit_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        data_requirement = base.DataRequirementFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:delete',
                        kwargs={'data_group_pk': data_group.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_data_requirement_edit_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_delete_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:add',
                        kwargs={'data_group_pk': data_group.pk}))

    def test_data_requirement_delete_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        data_requirement = base.DataRequirementFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:edit',
                        kwargs={'data_group_pk': data_group.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_edit_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        data_requirement = base.DataRequirementFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data_group:requirement:delete',
                        kwargs={'data_group_pk': data_group.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_data_requirement_edit_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_delete_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data_group:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))