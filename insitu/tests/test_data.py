from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base
from insitu.documents import DataDoc

import datetime


class DataTests(base.FormCheckTestCase):
    fields = ['name', 'note', 'start_time_coverage', 'end_time_coverage']
    related_fields = ['update_frequency', 'coverage', 'timeliness',
                      'policy', 'data_type', 'data_format',
                      'quality_control_procedure', 'dissemination']
    many_to_many_fields = ['inspire_themes', 'essential_variables']
    required_fields = ['name', 'update_frequency', 'coverage', 'timeliness',
                      'policy', 'data_type', 'data_format',
                      'quality_control_procedure', 'inspire_themes',
                       'dissemination']

    def setUp(self):
        super().setUp()
        update_frequency = base.UpdateFrequencyFactory()
        coverage = base.CoverageFactory()
        timeliness = base.TimelinessFactory()
        policy = base.PolicyFactory()
        data_type = base.DataTypeFactory()
        data_format = base.DataFormatFactory()
        quality_control_procedure = base.QualityControlProcedureFactory()
        inspire_themes = [base.InspireThemeFactory(),base.InspireThemeFactory()]
        essential_variables = [base.EssentialVariableFactory(),
                               base.EssentialVariableFactory(),
                               base.EssentialVariableFactory()]
        dissemination = base.DisseminationFactory()

        self._DATA = {
            'name': 'TEST data',
            'note': 'TEST note',
            'update_frequency': update_frequency.pk,
            'coverage': coverage.pk,
            'timeliness': timeliness.pk,
            'policy': policy.pk,
            'data_type': data_type.pk,
            'data_format': data_format.pk,
            'quality_control_procedure': quality_control_procedure.pk,
            'inspire_themes': [inspire_theme.pk for inspire_theme
                               in inspire_themes],
            'start_time_coverage': datetime.date(day=1, month=1, year=2000),
            'end_time_coverage': datetime.date(day=1, month=1, year=2000),
            'essential_variables': [essential_variable.pk for
                                    essential_variable in
                                    essential_variables],
            'dissemination': dissemination.pk
        }
        user = base.UserFactory()
        base.CopernicususProviderFactory(user=user)
        self.client.force_login(user)

    def test_list_data_json(self):
        base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_data_json_filter(self):
        base.DataFactory(name="Test data", created_by=self.creator)
        base.DataFactory(name="Other data", created_by=self.creator)
        resp = self.client.get(reverse('data:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_data(self):
        base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:list'))
        self.assertTemplateUsed(resp, 'data/list.html')

    def test_detail_data(self):
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:detail',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.context['data'], data)

    def test_get_edit_data(self):
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:edit',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_data(self):
        data_factory = base.DataFactory(created_by=self.creator)
        data = self._DATA
        resp = self.client.post(
            reverse('data:edit', kwargs={'pk': data_factory.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Data, data)

    def test_get_delete_data(self):
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:delete',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_data(self):
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.post(
            reverse('data:delete', kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.Data)
        self.check_objects_are_soft_deleted(models.Data, DataDoc)

    def test_delete_data_related_objects(self):
        data = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        base.DataRequirementFactory(data=data,
                                    requirement=requirement,
                                    created_by=self.creator
        )
        data_provider = base.DataProviderFactory(created_by=self.creator)
        base.DataProviderRelationFactory(data=data,
                                         provider=data_provider,
                                         created_by=self.creator)
        self.client.post(
            reverse('data:delete', kwargs={'pk': data.pk})
        )
        self.check_objects_are_soft_deleted(models.DataRequirement)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)


class DataPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.redirect_group_url = reverse('data:list')
        self.redirect_login_url = reverse('auth:login')

    def test_list_data_json_non_auth(self):
        self.check_permission_denied(method='GET',
                                     url=reverse('data:json'))

    def test_list_data_non_auth(self):
        self.check_user_redirect(method='GET',
                                 url=reverse('data:list'),
                                 redirect_url=self.redirect_login_url)

    def test_detail_data_non_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_user_redirect(method='GET',
                                 url=reverse('data:detail',
                                             kwargs={'pk': data.pk}),
                                 redirect_url=self.redirect_login_url)

    def test_add_data_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('data:add'),
            redirect_url=self.redirect_login_url)

    def test_edit_network_data_non_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('data:edit',
                        kwargs={'pk': data.pk}),
            redirect_url=self.redirect_login_url)

    def test_delete_network_data_non_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('data:delete',
                        kwargs={'pk': data.pk}),
            redirect_url=self.redirect_login_url)

    def test_add_data_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data:add'),
            redirect_url=self.redirect_group_url)

    def test_edit_network_data_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data:edit',
                        kwargs={'pk': data.pk}),
            redirect_url=self.redirect_group_url)

    def test_delete_network_data_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data:delete',
                        kwargs={'pk': data.pk}),
            redirect_url=self.redirect_group_url)
