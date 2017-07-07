from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class DataResponsibleRelationTests(base.FormCheckTestCase):
    fields = ['role']
    related_fields = ['data_group', 'responsible']
    required_fields = ['role', 'data_group', 'responsible']

    def setUp(self):
        super().setUp()
        data_group = base.DataGroupFactory()
        countries = [base.CountryFactory(code='T1'),
                     base.CountryFactory(code='T2')]
        responsible = base.DataResponsibleFactory(countries=countries)

        self._DATA = {
            'role': 1,
            'data_group': data_group.pk,
            'responsible': responsible.pk
        }
        user = base.UserFactory()
        base.CopernicususResponsibleFactory(user=user)
        self.client.force_login(user)

    def test_responsible_relation_add_required_fields_from_data_group(self):
        data = {}
        data_group = base.DataGroupFactory()
        errors_data_group = self.errors.copy()
        errors_data_group.pop('data_group')
        resp = self.client.post(reverse('data_group:responsible:add',
                                        kwargs={'group_pk': data_group.pk}),
                                data)
        self.check_required_errors(resp, errors_data_group)

    def test_responsible_relation_add_required_fields_from_data_responsible(self):
        data = {}
        data_responsible = base.DataResponsibleFactory()
        errors_data_responsible = self.errors.copy()
        errors_data_responsible.pop('responsible')

        resp = self.client.post(reverse('responsible:group:add',
                                        kwargs={'responsible_pk': data_responsible.pk}),
                                data)
        self.check_required_errors(resp, errors_data_responsible)

    def test_responsible_relation_add_from_data_group(self):
        data = self._DATA
        resp = self.client.post(reverse('data_group:responsible:add',
                                        kwargs={'group_pk': self._DATA['data_group']}),
                                data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_add_from_data_responsible(self):
        data = self._DATA
        resp = self.client.post(
            reverse('responsible:group:add',
                    kwargs={'responsible_pk': self._DATA['responsible']}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_edit_from_data_group(self):
        responsible_relation = base.DataResponsibleRelationFactory()
        data = self._DATA
        data.pop('data_group')
        data.pop('responsible')
        resp = self.client.post(
            reverse('data_group:responsible:edit',
                    kwargs={'group_pk': responsible_relation.data_group.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data_group'] = responsible_relation.data_group.pk
        data['responsible'] = responsible_relation.responsible.pk
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_edit_from_data_responsible(self):
        responsible_relation =base.DataResponsibleRelationFactory()
        data = self._DATA
        data.pop('data_group')
        data.pop('responsible')
        resp = self.client.post(
            reverse('responsible:group:edit',
                    kwargs={'responsible_pk': responsible_relation.responsible.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data_group'] = responsible_relation.data_group.pk
        data['responsible'] = responsible_relation.responsible.pk
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_delete_from_data_group(self):
        data = {}
        responsible_relation =base.DataResponsibleRelationFactory()
        resp = self.client.post(
            reverse('data_group:responsible:delete',
                    kwargs={'group_pk': responsible_relation.data_group.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataResponsibleRelation)

    def test_responsible_relation_delete_from_data_responsible(self):
        data = {}
        responsible_relation =base.DataResponsibleRelationFactory()
        resp = self.client.post(
            reverse('responsible:group:delete',
                    kwargs={'responsible_pk': responsible_relation.responsible.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataResponsibleRelation)


class DataResponsibleRelationPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.redirect_data_group_url = reverse('data_group:list')
        self.redirect_data_responsible_url = reverse('responsible:list')

    def test_responsible_relation_add_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:add',
                        kwargs={'group_pk': data_group.pk}))

    def test_responsible_relation_delete_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:edit',
                        kwargs={'group_pk': data_group.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_edit_not_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:delete',
                        kwargs={'group_pk': data_group.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_add_not_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:add',
                        kwargs={'responsible_pk': data_responsible.pk}))

    def test_responsible_relation_edit_not_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            responsible=data_responsible)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:edit',
                        kwargs={'responsible_pk': data_responsible.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_delete_not_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            responsible=data_responsible)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:delete',
                        kwargs={'responsible_pk': data_responsible.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_add_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:add',
                        kwargs={'group_pk': data_group.pk}))

    def test_responsible_relation_delete_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:edit',
                        kwargs={'group_pk': data_group.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_edit_auth_from_data_group(self):
        data_group = base.DataGroupFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data_group=data_group)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_group_url,
            url=reverse('data_group:responsible:delete',
                        kwargs={'group_pk': data_group.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_add_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:add',
                        kwargs={'responsible_pk': data_responsible.pk}))

    def test_responsible_relation_edit_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            responsible=data_responsible)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:edit',
                        kwargs={'responsible_pk': data_responsible.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_delete_auth_from_data_responsible(self):
        data_responsible = base.DataResponsibleFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            responsible=data_responsible)
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_data_responsible_url,
            url=reverse('responsible:group:delete',
                        kwargs={'responsible_pk': data_responsible.pk,
                                'pk': responsible_relation.pk}))