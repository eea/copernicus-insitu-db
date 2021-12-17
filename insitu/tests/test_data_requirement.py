from django.urls import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ["This field is required."]


class DataRequirementTests(base.FormCheckTestCase):
    fields = ["note", "information_costs", "handling_costs"]
    related_fields = ["data", "requirement", "level_of_compliance"]
    required_fields = ["data", "requirement", "level_of_compliance"]

    def setUp(self):
        super().setUp()
        self.data = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        self.requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        level_of_compliance = base.ComplianceLevelFactory()

        self._DATA = {
            "data": self.data.pk,
            "requirement": self.requirement.pk,
            "level_of_compliance": level_of_compliance.pk,
            "note": "TEST note",
            "information_costs": True,
            "handling_costs": True,
        }
        user = base.UserFactory(username="User DataRequirement")
        self.client.force_login(user)

    def test_data_requirement_add_required_fields(self):
        data = {}
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        errors_requirement = self.errors.copy()
        errors_requirement.pop("requirement")

        resp = self.client.post(
            reverse("requirement:data:add", kwargs={"requirement_pk": requirement.pk}),
            data,
        )
        self.check_required_errors(resp, errors_requirement)

    def test_get_data_requirement_add(self):
        resp = self.client.get(
            reverse(
                "requirement:data:add",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_data_requirement_add(self):
        data = self._DATA
        resp = self.client.post(
            reverse(
                "requirement:data:add",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.DataRequirement, data)

    def test_data_requirement_add_unique(self):
        base.DataRequirementFactory(
            data=self.data, requirement=self.requirement, created_by=self.creator
        )
        data = self._DATA
        resp = self.client.post(
            reverse(
                "requirement:data:add", kwargs={"requirement_pk": self.requirement.pk}
            ),
            data,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["form"].errors, {"__all__": ["This relation already exists."]}
        )

    def test_get_data_requirement_edit(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        resp = self.client.get(
            reverse(
                "requirement:data:edit",
                kwargs={
                    "requirement_pk": data_requirement.requirement.pk,
                    "pk": data_requirement.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_data_requirement_edit(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        data = self._DATA
        data.pop("data")
        data.pop("requirement")
        resp = self.client.post(
            reverse(
                "requirement:data:edit",
                kwargs={
                    "requirement_pk": data_requirement.requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        data["data"] = data_requirement.data.pk
        data["requirement"] = data_requirement.requirement.pk
        self.check_single_object(models.DataRequirement, data)

    def test_get_data_requirement_delete(self):
        self.login_creator()
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        resp = self.client.get(
            reverse(
                "requirement:data:delete",
                kwargs={
                    "requirement_pk": data_requirement.requirement.pk,
                    "pk": data_requirement.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_data_requirement_delete(self):
        self.login_creator()
        data = {}
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        resp = self.client.post(
            reverse(
                "requirement:data:delete",
                kwargs={
                    "requirement_pk": data_requirement.requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataRequirement)


class DataRequirementPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse("auth:login")

    def test_data_requirement_add_not_auth_from_data_requirement(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:data:add", kwargs={"requirement_pk": requirement.pk}
            ),
        )

    def test_data_requirement_edit_not_auth_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:data:edit",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )

    def test_data_requirement_edit_auth_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:data:edit",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )

    def test_data_requirement_edit_teammate_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "requirement:data:edit",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )

    def test_data_requirement_delete_not_auth_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:data:delete",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )

    def test_data_requirement_delete_auth_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:data:delete",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )

    def test_data_requirement_delete_teammate_from_data_requirement(self):
        data_object = base.DataFactory(created_by=self.creator)
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        data_requirement = base.DataRequirementFactory(
            data=data_object,
            requirement=requirement,
            created_by=self.creator,
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "requirement:data:delete",
                kwargs={
                    "requirement_pk": data_requirement.pk,
                    "pk": data_requirement.pk,
                },
            ),
        )
