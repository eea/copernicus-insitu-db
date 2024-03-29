import os

from django.core.management import call_command
from django.urls import reverse

from insitu import models
from insitu.documents import RequirementDoc
from insitu.tests import base


class RequirementTests(base.FormCheckTestCase):
    fields = ["name", "note"]
    related_fields = ["dissemination", "quality_control_procedure"]
    required_fields = ["name", "dissemination", "quality_control_procedure", "group"]
    related_entities_updated = [
        "uncertainty",
        "update_frequency",
        "timeliness",
        "horizontal_resolution",
        "vertical_resolution",
    ]
    many_to_many_fields = [
        "essential_variables",
    ]
    related_entities_updated_int = ["scale"]
    related_entities_fields = ["threshold", "breakthrough", "goal"]
    target_type = "requirement"

    def setUp(self):
        super().setUp()
        dissemination = base.DisseminationFactory()
        quality_control_procedure = base.QualityControlProcedureFactory()
        group = base.RequirementGroupFactory()
        essential_variables = [
            base.EssentialVariableFactory(),
            base.EssentialVariableFactory(),
            base.EssentialVariableFactory(),
        ]
        self.creator = base.UserFactory(username="New User 1")
        self.client.force_login(self.creator)
        self._DATA = {
            "name": "TEST requirement",
            "note": "TEST note",
            "owner": "TEST owner",
            "dissemination": dissemination.pk,
            "quality_control_procedure": quality_control_procedure.pk,
            "essential_variables": [
                essential_variable.pk for essential_variable in essential_variables
            ],
            "group": group.pk,
        }

        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                self._DATA["__".join([entity, field])] = ""
        for entity in self.related_entities_updated_int:
            for field in self.related_entities_fields:
                self._DATA["__".join([entity, field])] = ""
        self._DATA["uncertainty__goal"] = "1"

        self.cloned_errors = {}
        self.cloned_errors["__all__"] = [
            "This requirement is a duplicate. Please use the existing requirement."
        ]
        self.errors["__all__"] = ["At least one metric is required."]

        with open(os.devnull, "w") as f:
            call_command("search_index", "--rebuild", "-f", stdout=f)

    def _create_clone_data(self, requirement):
        REQUIREMENT_FOR_CLONE = {
            "name": requirement.name,
            "owner": requirement.owner,
            "dissemination": requirement.dissemination.pk,
            "note": requirement.note,
            "quality_control_procedure": requirement.quality_control_procedure.pk,
            "group": requirement.group.pk,
            "essential_variables": [],
        }
        for entity in self.related_entities_updated:
            for field in self.related_entities_fields:
                REQUIREMENT_FOR_CLONE["__".join([entity, field])] = getattr(
                    getattr(requirement, entity), field
                )
        for entity in self.related_entities_updated_int:
            for field in self.related_entities_fields:
                REQUIREMENT_FOR_CLONE["__".join([entity, field])] = getattr(
                    getattr(requirement, entity), field
                )
        return REQUIREMENT_FOR_CLONE

    def test_list_requirement_json(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(created_by=self.creator, **metrics)
        resp = self.client.get(reverse("requirement:json"))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertEqual(data["recordsTotal"], data["recordsFiltered"])

    def test_list_requirement_json_filter(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )

        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(
            name="Other requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(reverse("requirement:json"), {"search[value]": "Other"})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertFalse(data["recordsTotal"] < 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_requirement_json_filter_id(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(
            id=5, name="Test requirement", created_by=self.creator, **metrics
        )

        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(
            id=10, name="Other requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(reverse("requirement:json"), {"search[value]": 5})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertFalse(data["recordsTotal"] < 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_requirement_json_filter_component(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        req1 = base.RequirementFactory(
            name="First requirement", created_by=self.creator, **metrics
        )
        base.ProductRequirementFactory(
            requirement=req1,
            created_by=self.creator,
            product__name="Product 1",
            product__component__name="Component 1",
        )

        metrics = base.RequirementFactory.create_metrics(self.creator)
        req2 = base.RequirementFactory(
            name="Second requirement", created_by=self.creator, **metrics
        )
        base.ProductRequirementFactory(
            requirement=req2,
            product__name="Product 2",
            product__component__name="Component 2",
            created_by=self.creator,
        )
        resp = self.client.get(
            reverse("requirement:json"), {"component": "Component 1"}
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIs(data["recordsTotal"], 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_requirements(self):
        self.erase_logging_file()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(reverse("requirement:list"))
        self.assertTemplateUsed(resp, "requirement/list.html")
        self.logging()

    def test_detail_requirement(self):
        self.erase_logging_file()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(
            reverse("requirement:detail", kwargs={"pk": requirement.pk})
        )
        self.assertEqual(resp.context["requirement"], requirement)
        self.logging()

    def test_create_requirement_fields_required(self):
        data = {}
        resp = self.client.post(reverse("requirement:add"), data)
        self.check_required_errors(resp, self.errors)
        self.check_logged_action("tried to create")

    def test_get_create_requirement(self):
        resp = self.client.get(reverse("requirement:add"))
        self.assertEqual(resp.status_code, 200)

    def test_create_requirement(self):
        self.erase_logging_file()
        data = self._DATA
        resp = self.client.post(reverse("requirement:add"), data)
        self.assertEqual(resp.status_code, 302)
        obj = self.check_single_object(models.Requirement, data)
        self.check_logged_action("created", obj)
        self.logging()

    def test_get_add_with_clone(self):
        self.erase_logging_file()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        requirement.essential_variables.add(base.EssentialVariableFactory().id)
        requirement.save()
        resp = self.client.get(reverse("requirement:add"), {"pk": requirement.pk})
        self.assertEqual(resp.status_code, 200)
        form_data = [value for field, value in resp.context["form"].initial.items()]
        for value in form_data:
            self.assertTrue(value)
        self.logging()

    def test_post_add_with_clone_duplicate_error(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        cloned_data = self._create_clone_data(requirement)
        resp = self.client.post(
            reverse("requirement:add") + "?pk=" + str(requirement.pk), cloned_data
        )
        self.check_logged_action(
            "tried to clone object {pk} of".format(pk=requirement.pk), requirement
        )
        self.assertEqual(resp.context["form"].errors, self.cloned_errors)

    def test_post_add_with_clone(self):
        self.erase_logging_file()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        cloned_data = self._create_clone_data(requirement)
        cloned_data["name"] = "Updated requirement"

        resp = self.client.post(
            reverse("requirement:add") + "?pk=" + str(requirement.pk), cloned_data
        )
        self.assertEqual(resp.status_code, 200)
        self.check_logged_action(
            "tried to clone object {pk} of".format(pk=requirement.pk), requirement
        )

        cloned_data["uncertainty__threshold"] = "test threshold 2"
        resp = self.client.post(
            reverse("requirement:add") + "?pk=" + str(requirement.pk), cloned_data
        )
        new_requirement = models.Requirement.objects.last()
        self.check_logged_action(
            "cloned requirement {pk} to".format(pk=requirement.pk), new_requirement, 2
        )
        requirement.delete()
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.Requirement, cloned_data)
        self.logging()

    def test_get_edit_requirement(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(
            reverse("requirement:edit", kwargs={"pk": requirement.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_edit_requirement(self):
        self.login_creator()
        self.erase_logging_file()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        data = self._DATA
        resp = self.client.post(
            reverse("requirement:edit", kwargs={"pk": requirement.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        obj = self.check_single_object(models.Requirement, data)
        self.check_logged_action("updated", obj)
        self.logging()

    def test_get_delete_requirement(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(
            reverse("requirement:delete", kwargs={"pk": requirement.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_delete_requirement(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.post(
            reverse("requirement:delete", kwargs={"pk": requirement.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.Requirement)
        self.check_logged_action("deleted", requirement)
        self.check_objects_are_soft_deleted(models.Requirement, RequirementDoc)

    def test_delete_requirement_related_objects(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        data = base.DataFactory(created_by=self.creator)
        base.DataRequirementFactory(
            requirement=requirement, data=data, created_by=self.creator
        )
        self.client.post(reverse("requirement:delete", kwargs={"pk": requirement.pk}))
        self.check_logged_action("deleted", requirement)
        self.check_objects_are_soft_deleted(models.ProductRequirement)
        self.check_objects_are_soft_deleted(models.DataRequirement)

    def test_transition(self):
        self.erase_logging_file()
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        data = base.DataFactory(name="Test data", created_by=self.creator)
        data_requirement = base.DataRequirementFactory(
            data=data, created_by=self.creator, requirement=requirement
        )

        items = [requirement, data_requirement]
        for item in items:
            self.assertEqual(getattr(item, "state"), "draft")

        transitions = [
            {
                "source": "draft",
                "target": "ready",
                "transition": "mark_as_ready",
                "user": self.creator,
            },
            {
                "source": "ready",
                "target": "draft",
                "transition": "cancel",
                "user": self.creator,
            },
            {
                "source": "draft",
                "target": "ready",
                "transition": "mark_as_ready",
                "user": self.creator,
            },
            {
                "source": "ready",
                "target": "changes",
                "transition": "request_changes",
                "user": self.other_user,
            },
            {
                "source": "changes",
                "target": "draft",
                "transition": "make_changes",
                "user": self.creator,
            },
            {
                "source": "draft",
                "target": "ready",
                "transition": "mark_as_ready",
                "user": self.creator,
            },
            {
                "source": "ready",
                "target": "valid",
                "transition": "validate",
                "user": self.other_user,
            },
            {
                "source": "ready",
                "target": "valid",
                "transition": "validate",
                "user": self.creator,
            },
        ]

        for idx, transition in enumerate(transitions):
            for item in items:
                self.assertEqual(getattr(item, "state"), transition["source"])
            self.client.force_login(transition["user"])
            response = self.client.post(
                reverse(
                    "requirement:transition",
                    kwargs={
                        "source": transition["source"],
                        "target": transition["target"],
                        "transition": transition["transition"],
                        "pk": requirement.pk,
                    },
                )
            )
            self.assertRedirects(
                response, reverse("requirement:detail", kwargs={"pk": requirement.pk})
            )
            for item in items:
                getattr(item, "refresh_from_db")()
                self.assertEqual(getattr(item, "state"), transition["target"])
            if transition["target"] == "valid":
                for item in items:
                    item.state = transition["source"]
                    item.save()
            self.check_logged_action(
                "changed state from {source} to {target} for".format(
                    source=transition["source"], target=transition["target"]
                ),
                requirement,
                idx + 1,
            )
        self.logging(check_username=False)

    def test_transition_with_draft_data(self):
        self.erase_logging_file()
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        data = base.DataFactory(
            name="Test data", created_by=self.creator, update_frequency=None
        )
        data_requirement = base.DataRequirementFactory(
            data=data, created_by=self.creator, requirement=requirement
        )

        items = [requirement, data_requirement]
        for item in items:
            self.assertEqual(getattr(item, "state"), "draft")
        self.client.force_login(self.creator)
        response = self.client.get(
            reverse(
                "requirement:transition",
                kwargs={
                    "source": "draft",
                    "target": "ready",
                    "transition": "mark_as_ready",
                    "pk": requirement.pk,
                },
            )
        )
        self.assertTrue(response.status_code, 200)

    def test_transition_inexistent_state(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        data = base.DataFactory(name="Test data", created_by=self.creator)
        data_requirement = base.DataRequirementFactory(
            data=data, created_by=self.creator, requirement=requirement
        )
        provider = base.DataProviderFactory(
            name="Test provider", created_by=self.creator
        )
        data_provider = base.DataProviderRelationFactory(
            data=data, created_by=self.creator, provider=provider
        )

        items = [requirement, data, data_requirement, provider, data_provider]

        response = self.client.post(
            reverse(
                "requirement:transition",
                kwargs={
                    "source": "draft",
                    "target": "nosuchstate",
                    "transition": "nosuchtransition",
                    "pk": requirement.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, "refresh_from_db")()
            self.assertEqual(getattr(item, "state"), "draft")

    def test_transition_changes_requested_feedback(self):
        self.erase_logging_file()
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator, state="ready")
        requirement = base.RequirementFactory(
            name="Test requirement", state="ready", created_by=self.creator, **metrics
        )
        data = base.DataFactory(name="Test data", created_by=self.creator)
        data_requirement = base.DataRequirementFactory(
            data=data, state="ready", created_by=self.creator, requirement=requirement
        )

        items = [requirement, data_requirement]
        for item in items:
            self.assertEqual(getattr(item, "state"), "ready")

        self.client.force_login(self.other_user)
        self.client.post(
            reverse(
                "requirement:transition",
                kwargs={
                    "source": "ready",
                    "target": "changes",
                    "transition": "request_changes",
                    "pk": requirement.pk,
                },
            ),
            {"feedback": "this is a feedback test"},
        )
        getattr(requirement, "refresh_from_db")()

        self.check_logged_action(
            "changed state from ready to changes for", requirement
        )

        self.assertEqual(requirement.state, "changes")
        self.assertEqual(requirement.feedback, "this is a feedback test")


class RequirementPermissionTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.redirect_url = reverse("requirement:list")
        self.methods = ["GET", "POST"]

    def test_list_requirement_json_non_auth(self):
        resp = self.client.get(reverse("requirement:json"))
        self.assertEqual(resp.status_code, 200)

    def test_requirement_list_not_auth(self):
        resp = self.client.get(reverse("requirement:list"))
        self.assertEqual(resp.status_code, 200)

    def test_requirement_detail_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        resp = self.client.get(
            reverse("requirement:detail", kwargs={"pk": requirement.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_requirement_add_not_auth(self):
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("requirement:add"),
        )

    def test_requirement_edit_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("requirement:edit", kwargs={"pk": requirement.pk}),
        )

    def test_requirement_edit_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse("requirement:edit", kwargs={"pk": requirement.pk}),
        )

    def test_requirement_edit_teammate(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("requirement:edit", kwargs={"pk": requirement.pk}),
        )

    def test_requirement_delete_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("requirement:delete", kwargs={"pk": requirement.pk}),
        )

    def test_requirement_delete_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse("requirement:delete", kwargs={"pk": requirement.pk}),
        )

    def test_requirement_delete_teammate(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(
            name="Test requirement", created_by=self.creator, **metrics
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("requirement:delete", kwargs={"pk": requirement.pk}),
        )
