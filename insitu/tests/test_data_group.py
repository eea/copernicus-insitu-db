from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base
from insitu.documents import DataGroupDoc


class DataGroupTests(base.FormCheckTestCase):
    fields = ['name', 'note']
    related_fields = ['frequency', 'coverage', 'timeliness',
                      'policy', 'data_type', 'data_format',
                      'quality']
    many_to_many_fields = ['inspire_themes', 'essential_climate_variables']
    required_fields = ['name', 'frequency', 'coverage', 'timeliness',
                      'policy', 'data_type', 'data_format',
                      'quality', 'inspire_themes']

    def setUp(self):
        super().setUp()
        frequency = base.FrequencyFactory()
        coverage = base.CoverageFactory()
        timeliness = base.TimelinessFactory()
        policy = base.PolicyFactory()
        data_type = base.DataTypeFactory()
        data_format = base.DataFormatFactory()
        quality = base.QualityFactory()
        inspire_themes = [base.InspireThemeFactory(),base.InspireThemeFactory()]
        essential_climate_variables = [base.EssentialClimateVariableFactory(),
                                       base.EssentialClimateVariableFactory(),
                                       base.EssentialClimateVariableFactory()]

        self._DATA = {
            'name': 'TEST data group',
            'note': 'TEST note',
            'frequency': frequency.pk,
            'coverage': coverage.pk,
            'timeliness': timeliness.pk,
            'policy': policy.pk,
            'data_type': data_type.pk,
            'data_format': data_format.pk,
            'quality': quality.pk,
            'inspire_themes': [inspire_theme.pk for inspire_theme
                               in inspire_themes],
            'essential_climate_variables': [essential_climate_variable.pk for
                                            essential_climate_variable in
                                            essential_climate_variables]
        }
        user = base.UserFactory()
        base.CopernicususResponsibleFactory(user=user)
        self.client.force_login(user)

    def test_list_data_group_json(self):
        base.DataGroupFactory()
        resp = self.client.get(reverse('data_group:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_data_group_json_filter(self):
        base.DataGroupFactory(name="Test data group")
        base.DataGroupFactory(name="Other data group")
        resp = self.client.get(reverse('data_group:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_data_groups(self):
        base.DataGroupFactory()
        resp = self.client.get(reverse('data_group:list'))
        self.assertTemplateUsed(resp, 'data_group/list.html')

    def test_detail_data_group(self):
        data_group = base.DataGroupFactory()
        resp = self.client.get(reverse('data_group:detail',
                                       kwargs={'pk': data_group.pk}))
        self.assertEqual(resp.context['data_group'], data_group)


    def test_edit_data_group(self):
        data_group = base.DataGroupFactory()
        data = self._DATA
        resp = self.client.post(
            reverse('data_group:edit', kwargs={'pk': data_group.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataGroup, data)

    def test_delete_data_group(self):
        data_group = base.DataGroupFactory()
        resp = self.client.post(
            reverse('data_group:delete', kwargs={'pk': data_group.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataGroup)
        self.check_objects_are_soft_deleted(models.DataGroup, DataGroupDoc)

    def test_delete_data_group_related_objects(self):
        data_group = base.DataGroupFactory()
        base.DataRequirementFactory(data_group=data_group)
        base.DataResponsibleRelationFactory(data_group=data_group)
        self.client.post(
            reverse('data_group:delete', kwargs={'pk': data_group.pk})
        )
        self.check_objects_are_soft_deleted(models.DataRequirement)
        self.check_objects_are_soft_deleted(models.DataResponsibleRelation)


class DataGroupPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        self.redirect_group_url = reverse('data_group:list')
        self.redirect_login_url = reverse('auth:login')

    def test_list_data_group_json_non_auth(self):
        self.check_permission_denied(method='GET',
                                     url=reverse('data_group:json'))

    def test_list_data_groups_non_auth(self):
        self.check_user_redirect(method='GET',
                                 url=reverse('data_group:list'),
                                 redirect_url=self.redirect_login_url)

    def test_detail_data_group_non_auth(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect(method='GET',
                                 url=reverse('data_group:detail',
                                             kwargs={'pk': data_group.pk}),
                                 redirect_url=self.redirect_login_url)

    def test_add_data_group_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse('data_group:add'),
            redirect_url=self.redirect_login_url)

    def test_edit_network_data_group_non_auth(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            url=reverse('data_group:edit',
                        kwargs={'pk': data_group.pk}),
            redirect_url=self.redirect_login_url)

    def test_delete_network_data_group_non_auth(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            url=reverse('data_group:delete',
                        kwargs={'pk': data_group.pk}),
            redirect_url=self.redirect_login_url)

    def test_add_data_group_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data_group:add'),
            redirect_url=self.redirect_group_url)

    def test_edit_network_data_group_auth(self):
        data_group = base.DataGroupFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data_group:edit',
                        kwargs={'pk': data_group.pk}),
            redirect_url=self.redirect_group_url)

    def test_delete_network_data_group_auth(self):
        data_group = base.DataGroupFactory()
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data_group:delete',
                        kwargs={'pk': data_group.pk}),
            redirect_url=self.redirect_group_url)
