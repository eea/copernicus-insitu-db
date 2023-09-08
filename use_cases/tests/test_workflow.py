import os

from django.core.management import call_command
from django.urls import reverse

from use_cases.tests.factories import UseCaseFactory
from insitu.tests import base


class UseCaseWorkflowTests(base.FormCheckTestCase):
    fields = ["name", "note"]
    related_fields = ["dissemination", "quality_control_procedure"]
    required_fields = [
        "title",
        "data_provider",
        "data",
        "image_description",
        "description",
        "region",
        "locality",
    ]
    target_type = "use_case"

    def setUp(self):
        super().setUp()
        dissemination = base.DisseminationFactory()
        quality_control_procedure = base.QualityControlProcedureFactory()
        group = base.RequirementGroupFactory()
        self.creator = base.UserFactory(username="New User 1")
        self.client.force_login(self.creator)
        self._DATA = {
            "name": "TEST requirement",
            "note": "TEST note",
            "owner": "TEST owner",
            "dissemination": dissemination.pk,
            "quality_control_procedure": quality_control_procedure.pk,
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

    def test_transition(self):
        self.erase_logging_file()
        self.login_creator()
        use_case = UseCaseFactory(created_by=self.creator)
        self.assertEqual(getattr(use_case, "state"), "draft")

        transitions = [
            {
                "source": "draft",
                "target": "publication_requested",
                "transition": "request_publication",
                "user": self.creator,
            },
            {
                "source": "publication_requested",
                "target": "draft",
                "transition": "return_to_draft",
                "user": self.creator,
            },
            {
                "source": "draft",
                "target": "publication_requested",
                "transition": "request_publication",
                "user": self.creator,
            },
            {
                "source": "publication_requested",
                "target": "changes",
                "transition": "request_changes",
                "user": self.publisher,
            },
            {
                "source": "changes",
                "target": "draft",
                "transition": "return_to_draft",
                "user": self.creator,
            },
            {
                "source": "draft",
                "target": "publication_requested",
                "transition": "request_publication",
                "user": self.creator,
            },
            {
                "source": "publication_requested",
                "target": "published",
                "transition": "publish",
                "user": self.publisher,
            },
            {
                "source": "published",
                "target": "draft",
                "transition": "return_to_draft",
                "user": self.publisher,
            },
        ]

        for idx, transition in enumerate(transitions):
            self.assertEqual(getattr(use_case, "state"), transition["source"])
            self.client.force_login(transition["user"])
            response = self.client.post(
                reverse(
                    "use_cases:transition",
                    kwargs={
                        "source": transition["source"],
                        "target": transition["target"],
                        "transition": transition["transition"],
                        "pk": use_case.pk,
                    },
                )
            )
            self.assertRedirects(
                response, reverse("use_cases:detail", kwargs={"pk": use_case.pk})
            )
            getattr(use_case, "refresh_from_db")()
            self.assertEqual(getattr(use_case, "state"), transition["target"])
            if transition["target"] == "valid":
                use_case.state = transition["source"]
                use_case.save()
            self.check_logged_action(
                "changed state from {source} to {target} for".format(
                    source=transition["source"], target=transition["target"]
                ),
                use_case,
                idx + 1,
            )
        self.logging(check_username=False)

    def test_transition_inexistent_state(self):
        self.login_creator()
        use_case = UseCaseFactory(created_by=self.creator)
        self.assertEqual(getattr(use_case, "state"), "draft")

        response = self.client.post(
            reverse(
                "use_cases:transition",
                kwargs={
                    "source": "draft",
                    "target": "nosuchstate",
                    "transition": "nosuchtransition",
                    "pk": use_case.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_transition_changes_requested_feedback(self):
        self.login_creator()
        use_case = UseCaseFactory(
            created_by=self.creator, state="publication_requested"
        )
        self.assertEqual(getattr(use_case, "state"), "publication_requested")

        self.client.force_login(self.publisher)
        self.client.post(
            reverse(
                "use_cases:transition",
                kwargs={
                    "source": "ready",
                    "target": "changes",
                    "transition": "request_changes",
                    "pk": use_case.pk,
                },
            ),
            {"feedback": "this is a feedback test"},
        )
        getattr(use_case, "refresh_from_db")()

        self.check_logged_action("changed state from ready to changes for", use_case)

        self.assertEqual(use_case.state, "changes")
        self.assertEqual(use_case.feedback, "this is a feedback test")
