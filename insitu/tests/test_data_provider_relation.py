from django.core.urlresolvers import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ["This field is required."]


class DataProviderRelationTests(base.FormCheckTestCase):
    fields = ["role"]
    related_fields = ["data", "provider"]
    required_fields = ["role", "data", "provider"]

    def setUp(self):
        super().setUp()
        self.data = base.DataFactory(created_by=self.creator)
        countries = [base.CountryFactory(code="T1"), base.CountryFactory(code="T2")]
        self.provider = base.DataProviderFactory(
            countries=countries, created_by=self.creator
        )

        self._DATA = {"role": 1, "data": self.data.pk, "provider": self.provider.pk}
        user = base.UserFactory(username="User DataProvider")
        self.client.force_login(user)

    def test_provider_relation_add_required_fields(self):
        data = {}
        data_factory = base.DataFactory(created_by=self.creator)
        errors_data = self.errors.copy()
        errors_data.pop("data")
        resp = self.client.post(
            reverse("data:provider:add", kwargs={"group_pk": data_factory.pk}), data
        )
        self.check_required_errors(resp, errors_data)

    def test_get_provider_relation_add(self):
        resp = self.client.get(
            reverse("data:provider:add", kwargs={"group_pk": self._DATA["data"]})
        )
        self.assertEqual(resp.status_code, 200)

    def test_provider_relation_add(self):
        data = self._DATA
        resp = self.client.post(
            reverse("data:provider:add", kwargs={"group_pk": self._DATA["data"]}), data
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataProviderRelation, data)

    def test_provider_relation_add_unique(self):
        base.DataProviderRelationFactory(
            data=self.data, provider=self.provider, created_by=self.creator
        )
        data = self._DATA
        resp = self.client.post(
            reverse("data:provider:add", kwargs={"group_pk": self.data.pk}), data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["form"].errors, {"__all__": ["This relation already exists."]}
        )

    def test_get_provider_relation_edit(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data_object,
            created_by=self.creator,
        )
        resp = self.client.get(
            reverse(
                "data:provider:edit",
                kwargs={
                    "group_pk": provider_relation.data.pk,
                    "pk": provider_relation.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_provider_relation_edit(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data_object,
            created_by=self.creator,
        )
        data = self._DATA
        data.pop("data")
        data.pop("provider")
        resp = self.client.post(
            reverse(
                "data:provider:edit",
                kwargs={
                    "group_pk": provider_relation.data.pk,
                    "pk": provider_relation.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        data["data"] = provider_relation.data.pk
        data["provider"] = provider_relation.provider.pk
        self.check_single_object(models.DataProviderRelation, data)

    def test_get_provider_relation_delete(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data_object,
            created_by=self.creator,
        )
        resp = self.client.get(
            reverse(
                "data:provider:delete",
                kwargs={
                    "group_pk": provider_relation.data.pk,
                    "pk": provider_relation.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_provider_relation_delete(self):
        self.login_creator()
        data = {}
        data_object = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data_object,
            created_by=self.creator,
        )
        resp = self.client.post(
            reverse(
                "data:provider:delete",
                kwargs={
                    "group_pk": provider_relation.data.pk,
                    "pk": provider_relation.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProviderRelation)


class DataProviderRelationPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse("auth:login")

    def test_provider_relation_add_not_auth(self):
        data = base.DataFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse("data:provider:add", kwargs={"group_pk": data.pk}),
        )

    def test_provider_relation_edit_not_auth(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse(
                "data:provider:edit",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )

    def test_provider_relation_edit_auth(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("data:list"),
            url=reverse(
                "data:provider:edit",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )

    def test_edit_provider_relation_teammate(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "data:provider:edit",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )

    def test_provider_relation_delete_not_auth(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.login_url,
            url=reverse(
                "data:provider:delete",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )

    def test_provider_relation_delete_auth(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("data:list"),
            url=reverse(
                "data:provider:delete",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )

    def test_delete_provider_relation_teammate(self):
        data = base.DataFactory(created_by=self.creator)
        provider = base.DataProviderFactory(created_by=self.creator)
        provider_relation = base.DataProviderRelationFactory(
            provider=provider,
            data=data,
            created_by=self.creator,
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "data:provider:delete",
                kwargs={"group_pk": data.pk, "pk": provider_relation.pk},
            ),
        )
