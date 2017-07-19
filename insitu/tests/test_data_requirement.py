from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class DataRequirementTests(base.FormCheckTestCase):
    fields = ['note', 'information_costs', 'handling_costs']
    related_fields = ['data', 'requirement', 'level_of_compliance']
    required_fields = ['data', 'requirement', 'level_of_compliance']

    def setUp(self):
        super().setUp()
        data = base.DataFactory()
        requirement = base.RequirementFactory()
        level_of_compliance = base.ComplianceLevelFactory()

        self._DATA = {
            'data': data.pk,
            'requirement': requirement.pk,
            'level_of_compliance': level_of_compliance.pk,
            'note': 'TEST note',
            'information_costs': True,
            'handling_costs': True
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususResponsibleFactory(user=user)

    def test_data_requirement_add_required_fields_from_data(self):
        data = {}
        data_factory = base.DataFactory()
        errors_data = self.errors.copy()
        errors_data.pop('data')
        resp = self.client.post(
            reverse('data:requirement:add',
                    kwargs={'data_pk': data_factory.pk}),
            data)
        self.check_required_errors(resp, errors_data)

    def test_data_requirement_add_required_fields_from_requirement(self):
        data = {}
        requirement = base.RequirementFactory()
        errors_requirement = self.errors.copy()
        errors_requirement.pop('requirement')

        resp = self.client.post(
            reverse('requirement:data:add',
                    kwargs={'requirement_pk': requirement.pk}),
            data)
        self.check_required_errors(resp, errors_requirement)

    def test_data_requirement_add_from_data(self):
        data = self._DATA
        resp = self.client.post(
            reverse('data:requirement:add',
                    kwargs={'data_pk': self._DATA['data']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_add_from_requirement(self):
        data = self._DATA
        resp = self.client.post(
            reverse('requirement:data:add',
                    kwargs={'requirement_pk': self._DATA['requirement']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_edit_from_data(self):
        data_requirement = base.DataRequirementFactory()
        data = self._DATA
        data.pop('data')
        data.pop('requirement')
        resp = self.client.post(
            reverse('data:requirement:edit',
                    kwargs={'data_pk': data_requirement.data.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data'] = data_requirement.data.pk
        data['requirement'] = data_requirement.requirement.pk
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_edit_from_requirement(self):
        data_requirement = base.DataRequirementFactory()
        data = self._DATA
        data.pop('data')
        data.pop('requirement')
        resp = self.client.post(
            reverse('requirement:data:edit',
                    kwargs={'requirement_pk': data_requirement.requirement.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data'] = data_requirement.data.pk
        data['requirement'] = data_requirement.requirement.pk
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_delete_from_data(self):
        data = {}
        data_requirement = base.DataRequirementFactory()
        resp = self.client.post(
            reverse('data:requirement:delete',
                    kwargs={'data_pk': data_requirement.data.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataRequirement)

    def test_data_requirement_delete_from_requirement(self):
        data = {}
        data_requirement = base.DataRequirementFactory()
        resp = self.client.post(
            reverse('requirement:data:delete',
                    kwargs={'requirement_pk': data_requirement.requirement.pk,
                            'pk': data_requirement.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataRequirement)


class DataRequirementPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.login_url = reverse('auth:login')

    def test_data_requirement_add_not_auth_from_data(self):
        data = base.DataFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:add',
                        kwargs={'data_pk': data.pk}))

    def test_data_requirement_delete_not_auth_from_data(self):
        data = base.DataFactory()
        data_requirement = base.DataRequirementFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:edit',
                        kwargs={'data_pk': data.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_edit_not_auth_from_data(self):
        data = base.DataFactory()
        data_requirement = base.DataRequirementFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:delete',
                        kwargs={'data_pk': data.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_data_requirement_edit_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_delete_not_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_auth_from_data(self):
        data = base.DataFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:add',
                        kwargs={'data_pk': data.pk}))

    def test_data_requirement_delete_auth_from_data(self):
        data = base.DataFactory()
        data_requirement = base.DataRequirementFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:edit',
                        kwargs={'data_pk': data.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_edit_auth_from_data(self):
        data = base.DataFactory()
        data_requirement = base.DataRequirementFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:requirement:delete',
                        kwargs={'data_pk': data.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_add_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:add',
                        kwargs={'requirement_pk': data_requirement.pk}))

    def test_data_requirement_edit_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:edit',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))

    def test_data_requirement_delete_auth_from_data_requirement(self):
        data_requirement = base.RequirementFactory()
        data_requirement = base.DataRequirementFactory(
            requirement=data_requirement)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('requirement:data:delete',
                        kwargs={'requirement_pk': data_requirement.pk,
                                'pk': data_requirement.pk}))
