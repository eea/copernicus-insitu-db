from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base
from insitu.documents import DataDoc

import datetime


class DataTests(base.FormCheckTestCase):
    fields = ['name', 'note', 'start_time_coverage', 'end_time_coverage']
    related_fields = ['update_frequency', 'area', 'timeliness',
                      'data_policy', 'data_type', 'data_format',
                      'quality_control_procedure', 'dissemination']
    many_to_many_fields = ['inspire_themes', 'essential_variables']
    required_fields = ['name', 'update_frequency', 'area', 'timeliness',
                       'data_policy', 'data_type', 'data_format',
                       'quality_control_procedure', 'dissemination']
    target_type = 'data'
    custom_errors = {
        'inspire_themes': [''],
        'essential_variables':
            ['At least one Inspire Theme or Essential Variable is required.']
    }

    def setUp(self):
        super().setUp()
        update_frequency = base.UpdateFrequencyFactory()
        area = base.AreaFactory()
        timeliness = base.TimelinessFactory()
        data_policy = base.DataPolicyFactory()
        data_type = base.DataTypeFactory()
        data_format = base.DataFormatFactory()
        quality_control_procedure = base.QualityControlProcedureFactory()
        inspire_themes = [base.InspireThemeFactory(),
                          base.InspireThemeFactory()]
        essential_variables = [base.EssentialVariableFactory(),
                               base.EssentialVariableFactory(),
                               base.EssentialVariableFactory()]
        dissemination = base.DisseminationFactory()

        self._DATA = {
            'name': 'TEST data',
            'note': 'TEST note',
            'update_frequency': update_frequency.pk,
            'area': area.pk,
            'timeliness': timeliness.pk,
            'data_policy': data_policy.pk,
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

        self.creator = base.UserFactory(username='User Data')
        self.client.force_login(self.creator)

    def _create_clone_data(self, data):
        inspire_themes = [base.InspireThemeFactory(),
                          base.InspireThemeFactory()]
        DATA_FOR_CLONE = {
            'name': data.name,
            'note': 'TEST note',
            'dissemination': data.dissemination.pk,
            'update_frequency': data.update_frequency.pk,
            'area': data.area.pk,
            'timeliness': data.timeliness.pk,
            'data_policy': data.data_policy.pk,
            'data_type': data.data_type.pk,
            'data_format': data.data_format.pk,
            'start_time_coverage': datetime.date(day=1, month=1, year=2000),
            'end_time_coverage': datetime.date(day=1, month=1, year=2000),
            'quality_control_procedure': data.quality_control_procedure.pk,
            'inspire_themes': [inspire_theme.pk for inspire_theme
                               in inspire_themes],
            'essential_variables': [],
        }
        return DATA_FOR_CLONE

    def test_list_data_json(self):
        base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:json'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertEqual(data['recordsTotal'], data['recordsFiltered'])

    def test_list_data_json_filter(self):
        base.DataFactory(name='Test data', created_by=self.creator)
        base.DataFactory(name='Other data', created_by=self.creator)
        resp = self.client.get(reverse('data:json'),
                               {'search[value]': 'Other'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data['recordsTotal'], 0)
        self.assertFalse(data['recordsTotal'] < 2)
        self.assertIs(data['recordsFiltered'], 1)

    def test_list_data(self):
        self.erase_logging_file()
        base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:list'))
        self.assertTemplateUsed(resp, 'data/list.html')
        self.logging()

    def test_get_add_data(self):
        resp = self.client.get(reverse('data:add'))
        self.assertEqual(resp.status_code, 200)

    def test_add_data_ready(self):
        data = {}
        resp = self.client.post(reverse('data:add') + '?ready', data)
        self.check_required_errors(resp, self.errors)

    def test_add_data_draft(self):
        data = {}
        resp = self.client.post(reverse('data:add'), data)
        self.errors = {'name': self.REQUIRED_ERROR}
        self.check_required_errors(resp, self.errors)

    def test_add_data(self):
        self.erase_logging_file()
        data = self._DATA
        resp = self.client.post(reverse('data:add'), data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Data, data)
        self.logging()

    def test_add_data_either_essential_variable_or_inspire_theme_required(self):
        self.erase_logging_file()
        data = self._DATA
        essential_variables = data.pop('essential_variables')
        inspire_themes = data.pop('inspire_themes')
        resp = self.client.post(reverse('data:add') + '?ready', data)

        self.assertEqual(resp.status_code, 200)
        self.assertIsNot(resp.context['form'].errors, {})
        self.assertDictEqual(
            resp.context['form'].errors,
            self.custom_errors
        )

        data['essential_variables'] = essential_variables
        data['inspire_themes'] = []
        resp = self.client.post(reverse('data:add'), data)
        self.assertEqual(resp.status_code, 302)
        self.check_object(models.Data.objects.first(), data)

        data['essential_variables'] = []
        data['inspire_themes'] = inspire_themes
        resp = self.client.post(reverse('data:add'), data)
        self.assertEqual(resp.status_code, 302)
        self.check_object(models.Data.objects.last(), data)
        self.logging()

    def test_get_add_with_clone(self):
        self.erase_logging_file()
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:add')  + '?ready&pk=' + str(data.pk),
                               {})
        self.assertEqual(resp.status_code, 200)
        form_data = [ value for field, value in resp.context['form'].initial.items()]
        self.assertTrue(form_data)
        self.logging()

    def test_get_add_clone_nonexistent_object(self):
        self.erase_logging_file()
        resp = self.client.get(reverse('data:add')  + '?ready&pk=20', {})
        self.assertEqual(resp.status_code, 200)

    def test_post_add_with_clone_ready_errors(self):
        data = base.DataFactory(created_by=self.creator)
        self._create_clone_data(data)
        resp = self.client.post(reverse('data:add')  + '?ready&pk=' + str(data.pk),
                                {})
        self.assertEqual(resp.status_code, 200)
        self.check_required_errors(resp, self.errors)

    def test_post_add_with_clone_ready(self):
        data = base.DataFactory(created_by=self.creator)
        cloned_data = self._create_clone_data(data)
        resp = self.client.post(reverse('data:add')  + '?ready&pk=' + str(data.pk),
                                cloned_data)
        self.assertEqual(resp.status_code, 302)
        self.check_object(models.Data.objects.last(), cloned_data)

    def test_post_add_clone_without_ready(self):
        data = base.DataFactory(created_by=self.creator)
        cloned_data = self._create_clone_data(data)
        resp = self.client.post(reverse('data:add') + '?pk=' + str(data.pk),
                                cloned_data)
        self.assertEqual(resp.status_code, 302)
        self.check_object(models.Data.objects.last(), cloned_data)

    def test_detail_data(self):
        self.erase_logging_file()
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:detail',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.context['data'], data)
        self.logging()

    def test_get_edit_data(self):
        self.login_creator()
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:edit',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_data(self):
        self.login_creator()
        self.erase_logging_file()
        data_factory = base.DataFactory(created_by=self.creator)
        data = self._DATA
        resp = self.client.post(
            reverse('data:edit', kwargs={'pk': data_factory.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Data, data)
        self.logging()
        resp = self.client.get(
            reverse('data:edit', kwargs={'pk': data_factory.pk}) + '?ready')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(
            reverse('data:edit', kwargs={'pk': data_factory.pk}) + '?ready',
            data
        )
        self.assertEqual(resp.status_code, 302)

    def test_get_delete_data(self):
        self.login_creator()
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.get(reverse('data:delete',
                                       kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_data(self):
        self.login_creator()
        self.erase_logging_file()
        data = base.DataFactory(created_by=self.creator)
        resp = self.client.post(
            reverse('data:delete', kwargs={'pk': data.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.Data)
        self.check_objects_are_soft_deleted(models.Data, DataDoc)
        self.logging()

    def test_delete_data_related_objects(self):
        self.login_creator()
        data = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator,
                                              **metrics)
        base.DataRequirementFactory(data=data,
                                    requirement=requirement,
                                    created_by=self.creator)
        data_provider = base.DataProviderFactory(created_by=self.creator)
        base.DataProviderRelationFactory(data=data,
                                         provider=data_provider,
                                         created_by=self.creator)
        self.client.post(
            reverse('data:delete', kwargs={'pk': data.pk})
        )
        self.check_objects_are_soft_deleted(models.DataRequirement)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)


    def test_transition(self):
        self.erase_logging_file()
        self.login_creator()
        data = base.DataFactory(name='Test data',
                                created_by=self.creator)
        provider = base.DataProviderFactory(name='Test provider',
                                            created_by=self.creator)
        data_provider = base.DataProviderRelationFactory(data=data,
                                                         created_by=self.creator,
                                                         provider=provider)
        items = ([data, data_provider])
        for item in items:
            self.assertEqual((getattr(item, 'state')).name, 'draft')

        transitions = [
            {'source': 'draft', 'target': 'ready', 'user': self.creator},
            {'source': 'ready', 'target': 'draft', 'user': self.creator},
            {'source': 'draft', 'target': 'ready', 'user': self.creator},
            {'source': 'ready', 'target': 'changes', 'user': self.other_user},
            {'source': 'changes', 'target': 'draft', 'user': self.creator},
            {'source': 'draft', 'target': 'ready', 'user': self.creator},
            {'source': 'ready', 'target': 'valid', 'user': self.other_user},
            {'source': 'ready', 'target': 'valid', 'user': self.creator},
        ]

        for transition in transitions:
            for item in items:
                self.assertEqual((getattr(item, 'state')).name, transition['source'])
            self.client.force_login(transition['user'])
            response = self.client.post(
                reverse('data:transition',
                        kwargs={'source': transition['source'],
                                'target': transition['target'],
                                'pk': data.pk}))
            self.assertRedirects(response, reverse('data:detail',
                                                   kwargs={'pk': data.pk}))
            for item in items:
                getattr(item, 'refresh_from_db')()
                self.assertEqual((getattr(item, 'state')).name, transition['target'])
            if transition['target'] == 'valid':
               for item in items:
                   item.state = transition['source']
                   item.save()
        self.logging(check_username=False)

    def test_transition_with_draft_data(self):
        self.erase_logging_file()
        self.login_creator()
        data = base.DataFactory(name='Test data',
                                created_by=self.creator)
        provider = base.DataProviderFactory(name='Test provider',
                                            created_by=self.creator)
        data_provider = base.DataProviderRelationFactory(data=data,
                                                         created_by=self.creator,
                                                         provider=provider)

        items = ([data, data_provider])
        for item in items:
            self.assertEqual((getattr(item, 'state')).name, 'draft')
        self.client.force_login(self.creator)
        response = self.client.get(
            reverse('data:transition',
                    kwargs={'source': 'draft',
                            'target': 'ready',
                            'pk': data.pk}))
        self.assertTrue(response.status_code, 200)

    def test_transition_inexistent_state(self):
        self.login_creator()
        data = base.DataFactory(name='Test data',
                                created_by=self.creator)
        provider = base.DataProviderFactory(name='Test provider',
                                            created_by=self.creator)
        data_provider = base.DataProviderRelationFactory(data=data,
                                                         created_by=self.creator,
                                                         provider=provider)
        items = ([data, data_provider])


        response = self.client.post(
            reverse('data:transition',
                    kwargs={'source': 'draft',
                            'target': 'nosuchstate',
                            'pk': data.pk}))
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, 'refresh_from_db')()
            self.assertEqual((getattr(item, 'state')).name, 'draft')


    def test_transition_existent_state_no_transition(self):
        self.login_creator()
        data = base.DataFactory(name='Test data',
                                created_by=self.creator)
        provider = base.DataProviderFactory(name='Test provider',
                                            created_by=self.creator)
        base.DataProviderRelationFactory(data=data,
                                         created_by=self.creator,
                                         provider=provider)

        items = ([data, provider])

        response = self.client.post(
            reverse('data:transition',
                    kwargs={'source': 'draft',
                            'target': 'valid',
                            'pk': data.pk}))
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, 'refresh_from_db')()
            self.assertEqual((getattr(item, 'state')).name, 'draft')


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

    def test_edit_network_data_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data:edit',
                        kwargs={'pk': data.pk}),
            redirect_url=reverse('data:list'))

    def test_edit_data_teammate(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_permission_for_teammate(method='GET',
                                           url=reverse('data:edit',
                                                       kwargs={'pk': data.pk}),)

    def test_delete_network_data_non_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse('data:delete',
                        kwargs={'pk': data.pk}),
            redirect_url=self.redirect_login_url)

    def test_delete_network_data_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse('data:delete',
                        kwargs={'pk': data.pk}),
            redirect_url=reverse('data:list'))

    def test_delete_data_teammate(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_permission_for_teammate(method='GET',
                                           url=reverse('data:delete',
                                                       kwargs={'pk': data.pk}))
