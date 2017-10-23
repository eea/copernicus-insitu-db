from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ['This field is required.']


class DataResponsibleRelationTests(base.FormCheckTestCase):
    fields = ['role']
    related_fields = ['data', 'responsible']
    required_fields = ['role', 'data', 'responsible']

    def setUp(self):
        super().setUp()
        data = base.DataFactory()
        countries = [base.CountryFactory(code='T1'),
                     base.CountryFactory(code='T2')]
        responsible = base.DataResponsibleFactory(countries=countries)

        self._DATA = {
            'role': 1,
            'data': data.pk,
            'responsible': responsible.pk
        }
        user = base.UserFactory()
        self.client.force_login(user)
        base.CopernicususResponsibleFactory(user=user)

    def test_responsible_relation_add_required_fields(self):
        data = {}
        data_factory = base.DataFactory()
        errors_data = self.errors.copy()
        errors_data.pop('data')
        resp = self.client.post(reverse('data:responsible:add',
                                        kwargs={'group_pk': data_factory.pk}),
                                data)
        self.check_required_errors(resp, errors_data)

    def test_responsible_relation_add(self):
        data = self._DATA
        resp = self.client.post(reverse('data:responsible:add',
                                        kwargs={'group_pk': self._DATA['data']}),
                                data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_edit(self):
        responsible_relation = base.DataResponsibleRelationFactory()
        data = self._DATA
        data.pop('data')
        data.pop('responsible')
        resp = self.client.post(
            reverse('data:responsible:edit',
                    kwargs={'group_pk': responsible_relation.data.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        data['data'] = responsible_relation.data.pk
        data['responsible'] = responsible_relation.responsible.pk
        self.check_single_object(models.DataResponsibleRelation, data)

    def test_responsible_relation_delete(self):
        data = {}
        responsible_relation =base.DataResponsibleRelationFactory()
        resp = self.client.post(
            reverse('data:responsible:delete',
                    kwargs={'group_pk': responsible_relation.data.pk,
                            'pk': responsible_relation.pk}),
            data)
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataResponsibleRelation)


class DataResponsibleRelationPermissionsTests(base.PermissionsCheckTestCase):

    def setUp(self):
        self.login_url = reverse('auth:login')

    def test_responsible_relation_add_not_auth(self):
        data = base.DataFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:add',
                        kwargs={'group_pk': data.pk}))

    def test_responsible_relation_delete_not_auth(self):
        data = base.DataFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:edit',
                        kwargs={'group_pk': data.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_edit_not_auth(self):
        data = base.DataFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:delete',
                        kwargs={'group_pk': data.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_add_auth(self):
        data = base.DataFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:add',
                        kwargs={'group_pk': data.pk}))

    def test_responsible_relation_delete_auth(self):
        data = base.DataFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:edit',
                        kwargs={'group_pk': data.pk,
                                'pk': responsible_relation.pk}))

    def test_responsible_relation_edit_auth(self):
        data = base.DataFactory()
        responsible_relation = base.DataResponsibleRelationFactory(
            data=data)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse('data:responsible:delete',
                        kwargs={'group_pk': data.pk,
                                'pk': responsible_relation.pk}))
