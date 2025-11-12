import os

from django.core.management import call_command
from django.urls import reverse

from insitu import models
from insitu.documents import DataProviderDoc
from insitu.tests import base
from insitu.utils import soft_deleted


class DataProviderTests(base.FormCheckTestCase):
    fields = ["name", "edmo", "is_network", "description"]
    many_to_many_fields = ["networks", "countries"]
    required_fields = ["name", "is_network", "countries"]
    target_type = "data provider"

    def setUp(self):
        super().setUp()
        countries = [
            base.CountryFactory(code="TST1"),
            base.CountryFactory(code="TST2"),
        ]

        self._DATA = {
            "name": "test name",
            "edmo": 234,
            "description": "test description",
            "countries": [country.pk for country in countries],
            "is_network": True,
        }

        self.details_fields = [
            "acronym",
            "website",
            "address",
            "phone",
            "email",
            "provider_type",
            "data_provider",
        ]

        self.details_required_fields = ["provider_type"]

        provider_type = base.ProviderTypeFactory()
        self._DETAILS_DATA = {
            "acronym": "acronym",
            "website": "http://test.website",
            "address": "test address",
            "phone": "test phone",
            "email": "test@email.com",
            "provider_type": provider_type.pk,
        }
        self.creator = base.UserFactory(username="New user 1")
        self.client.force_login(self.creator)

        with open(os.devnull, "w") as f:
            call_command("search_index", "--rebuild", "-f", stdout=f)

    def test_list_provider_json(self):
        base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse("provider:json"))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertEqual(data["recordsTotal"], data["recordsFiltered"])

    def test_list_provider_json_filter(self):
        base.DataProviderFactory(
            name="Test provider",
            created_by=self.creator,
            countries=[base.CountryFactory(code="RO")],
        )
        base.DataProviderFactory(
            name="Other provider",
            created_by=self.creator,
            countries=[base.CountryFactory(code="UK")],
        )
        resp = self.client.get(reverse("provider:json"), {"search[value]": "Other"})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertFalse(data["recordsTotal"] < 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_provider_json_filter_acronym(self):
        provider = base.DataProviderFactory(
            name="Acronym Test",
            created_by=self.creator,
            countries=[base.CountryFactory(code="RO")],
        )
        base.DataProviderDetailsFactory(
            acronym="TST", data_provider=provider, created_by=self.creator
        )
        other_provider = base.DataProviderFactory(
            name="Other Acronym Test",
            created_by=self.creator,
            countries=[base.CountryFactory(code="UK")],
        )
        base.DataProviderDetailsFactory(
            acronym="OTH", data_provider=other_provider, created_by=self.creator
        )

        resp = self.client.get(reverse("provider:json"), {"search[value]": "TST"})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertFalse(data["recordsTotal"] < 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_provider_json_filter_component(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        romania = base.CountryFactory(code="RO")

        # Create 4 components
        first_component = base.ComponentFactory(name="First component")
        second_component = base.ComponentFactory(name="Second component")
        common_component = base.ComponentFactory(name="Common component")
        other_component = base.ComponentFactory(name="Other component")

        # Create data provider
        dpr1 = base.DataProviderRelationFactory(
            created_by=self.creator,
            data__created_by=self.creator,
            provider__name="First provider",
            provider__created_by=self.creator,
            provider__countries=[romania],
        )
        requirement1 = base.RequirementFactory(created_by=self.creator, **metrics)
        data_req1 = base.DataRequirementFactory(
            created_by=self.creator,
            data=dpr1.data,
            requirement=requirement1,
        )
        # Associate it with first and common components
        prod_req1 = base.ProductRequirementFactory(
            created_by=self.creator,
            requirement=requirement1,
            product__component=first_component,
        )
        base.ProductRequirementFactory(
            created_by=self.creator,
            requirement=requirement1,
            product__component=common_component,
        )

        # Create a second data provider
        dpr2 = base.DataProviderRelationFactory(
            created_by=self.creator,
            data__created_by=self.creator,
            provider__name="Second provider",
            provider__created_by=self.creator,
            provider__countries=[romania],
        )
        requirement2 = base.RequirementFactory(created_by=self.creator, **metrics)
        base.DataRequirementFactory(
            created_by=self.creator,
            data=dpr2.data,
            requirement=requirement2,
        )
        # Associate it with second and common components
        base.ProductRequirementFactory(
            created_by=self.creator,
            requirement=requirement2,
            product__component=second_component,
        )
        base.ProductRequirementFactory(
            created_by=self.creator,
            requirement=requirement2,
            product__component=common_component,
        )

        # Create a third data provider
        dpr3 = base.DataProviderRelationFactory(
            created_by=self.creator,
            data__created_by=self.creator,
            provider__name="Third provider",
            provider__created_by=self.creator,
            provider__countries=[romania],
        )
        requirement3 = base.RequirementFactory(created_by=self.creator, **metrics)
        base.DataRequirementFactory(
            created_by=self.creator,
            data=dpr3.data,
            requirement=requirement3,
        )
        # Associate it with other component
        base.ProductRequirementFactory(
            created_by=self.creator,
            requirement=requirement3,
            product__component=other_component,
        )

        # Filter by component (First component)
        resp = self.client.get(
            reverse("provider:json"), {"component": "First component"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIs(data["recordsTotal"], 3)
        self.assertIs(data["recordsFiltered"], 1)

        # Filter by component (Second component)
        resp = self.client.get(
            reverse("provider:json"), {"component": "Second component"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIs(data["recordsTotal"], 3)
        self.assertIs(data["recordsFiltered"], 1)

        # Filter by component (Common component)
        resp = self.client.get(
            reverse("provider:json"), {"component": "Common component"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIs(data["recordsTotal"], 3)
        self.assertIs(data["recordsFiltered"], 2)

        objs_to_soft_delete = [
            dpr1.provider,
            dpr1,
            dpr1.data,
            data_req1,
            requirement1,
            prod_req1,
            prod_req1.product,
        ]
        # Soft delete intermediate objects
        for obj in objs_to_soft_delete:
            with soft_deleted(obj):
                resp = self.client.get(
                    reverse("provider:json"), {"component": "First component"}
                )
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                # No records are filtered
                self.assertIs(data["recordsFiltered"], 0)

    def test_list_providers(self):
        self.erase_logging_file()
        base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse("provider:list"))
        self.assertTemplateUsed(resp, "data_provider/list.html")
        self.logging()

    def test_detail_provider(self):
        self.erase_logging_file()
        provider = base.DataProviderFactory(is_network=True, created_by=self.creator)
        resp = self.client.get(reverse("provider:detail", kwargs={"pk": provider.pk}))
        self.assertEqual(resp.context["provider"], provider)
        self.logging()

    def test_detail_provider_non_network(self):
        self.erase_logging_file()
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        resp = self.client.get(reverse("provider:detail", kwargs={"pk": provider.pk}))
        self.assertEqual(resp.context["provider"], provider)
        self.logging()

    def test_add_network_provider_required_fields(self):
        data = {}
        resp = self.client.post(reverse("provider:add_network"), data)
        self.check_required_errors(resp, self.errors)
        self.check_logged_action("tried to create")

    def test_get_add_network_provider(self):
        resp = self.client.get(reverse("provider:add_network"))
        self.assertEqual(resp.status_code, 200)

    def test_add_network_provider(self):
        self.erase_logging_file()
        data = self._DATA
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        resp = self.client.post(reverse("provider:add_network"), data)
        self.assertEqual(resp.status_code, 302)
        data["networks"] = []
        obj = self.check_single_object(models.DataProvider, data)
        provider = models.DataProvider.objects.last()
        details = provider.details.first()
        details_data.pop("provider_type")
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, "provider_type").pk, data["provider_type"])
        self.logging()
        self.check_logged_action("created", obj)

    def test_get_edit_network_provider(self):
        self.login_creator()
        self.erase_logging_file()
        network = base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(
            reverse("provider:edit_network", kwargs={"pk": network.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.logging()

    def test_edit_network_provider(self):
        self.login_creator()
        self.erase_logging_file()
        data = self._DATA
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        network = base.DataProviderFactory(is_network=True, created_by=self.creator)
        details = base.DataProviderDetailsFactory(
            data_provider=network, created_by=self.creator
        )
        resp = self.client.post(
            reverse("provider:edit_network", kwargs={"pk": network.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        data["networks"] = []
        details.refresh_from_db()
        details_data.pop("provider_type")
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, "provider_type").pk, data["provider_type"])
        obj = self.check_single_object(models.DataProvider, data)
        self.logging()
        self.check_logged_action("updated", obj)

    def test_get_edit_network_members_provider(self):
        self.login_creator()
        network = base.DataProviderFactory(is_network=True, created_by=self.creator)
        resp = self.client.get(
            reverse("provider:edit_network_members", kwargs={"pk": network.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_edit_network_members_provider(self):
        self.login_creator()
        member_1 = base.DataProviderFactory(
            id=1,
            name="test member 1",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T1").pk],
        )
        member_2 = base.DataProviderFactory(
            id=2,
            name="test member 2",
            is_network=False,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T2").pk],
        )
        member_3 = base.DataProviderFactory(
            id=3,
            name="test member 3",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T3").pk],
        )
        network = base.DataProviderFactory(is_network=True, created_by=self.creator)
        data = dict()
        data["members"] = [member_1.pk, member_2.pk, member_3.pk]
        resp = self.client.post(
            reverse("provider:edit_network_members", kwargs={"pk": network.pk}), data
        )

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 3)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)
        self.assertEqual(network.members.get(id=member_2.pk).name, member_2.name)
        self.assertEqual(network.members.get(id=member_3.pk).name, member_3.name)

    def test_edit_network_members_validation_provider(self):
        self.login_creator()
        network = base.DataProviderFactory(
            id=1, created_by=self.creator, is_network=True
        )
        data = dict()
        data["members"] = [1]
        resp = self.client.post(
            reverse("provider:edit_network_members", kwargs={"pk": network.pk}), data
        )

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["form"].errors["__all__"][0],
            "Members should be different than the network.",
        )

    def test_delete_network_members_provider(self):
        self.login_creator()
        member_1 = base.DataProviderFactory(
            id=1,
            name="test member 1",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T1").pk],
        )
        member_2 = base.DataProviderFactory(
            id=2,
            name="test member 2",
            is_network=False,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T2").pk],
        )
        network = base.DataProviderFactory(
            id=3,
            is_network=True,
            created_by=self.creator,
        )
        network.members.set([member_1.pk, member_2.pk])
        data = dict()
        data["members"] = [member_1.pk]
        resp = self.client.post(
            reverse("provider:edit_network_members", kwargs={"pk": network.pk}), data
        )

        network.refresh_from_db()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(network.members.count(), 1)
        self.assertEqual(network.members.get(id=member_1.pk).name, member_1.name)

    def test_transition(self):
        self.erase_logging_file()
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=True, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        for item in items:
            self.assertEqual((getattr(item, "state")), "draft")

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
                    "provider:transition",
                    kwargs={
                        "source": transition["source"],
                        "target": transition["target"],
                        "transition": transition["transition"],
                        "pk": provider.pk,
                    },
                )
            )
            self.assertRedirects(
                response, reverse("provider:detail", kwargs={"pk": provider.pk})
            )
            for item in items:
                getattr(item, "refresh_from_db")()
                self.assertEqual((getattr(item, "state")), transition["target"])
            if transition["target"] == "valid":
                for item in items:
                    item.state = transition["source"]
                    item.save()
            self.check_logged_action(
                "changed state from {source} to {target} for".format(
                    source=transition["source"], target=transition["target"]
                ),
                provider,
                idx + 1,
            )
        self.logging(check_username=False)

    def test_transition_with_draft_data(self):
        self.erase_logging_file()
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=True, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        for item in items:
            self.assertEqual(getattr(item, "state"), "draft")
        self.client.force_login(self.creator)
        response = self.client.get(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "ready",
                    "transition": "mark_as_ready",
                    "pk": provider.pk,
                },
            )
        )
        self.assertTrue(response.status_code, 200)

    def test_transition_inexistent_state(self):
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=True, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        response = self.client.post(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "nosuchstate",
                    "transition": "nosuchtransition",
                    "pk": provider.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, "refresh_from_db")()
            self.assertEqual(getattr(item, "state"), "draft")

    def test_transition_existent_state_no_transition(self):
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=True, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        response = self.client.post(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "valid",
                    "transition": "notransition",
                    "pk": provider.pk,
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
        provider = base.DataProviderFactory(
            is_network=True,
            state="ready",
            name="Test provider",
            created_by=self.creator,
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, state="ready", created_by=self.creator
        )
        items = [provider, provider_details]
        for item in items:
            self.assertEqual(getattr(item, "state"), "ready")

        self.client.force_login(self.other_user)
        self.client.post(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "ready",
                    "target": "changes",
                    "transition": "request_changes",
                    "pk": provider.pk,
                },
            ),
            {"feedback": "this is a feedback test"},
        )
        getattr(provider, "refresh_from_db")()
        self.assertEqual(provider.state, "changes")
        self.assertEqual(provider.feedback, "this is a feedback test")
        self.check_logged_action("changed state from ready to changes for", provider)

    def test_get_add_non_network_provider_required_fields(self):
        resp = self.client.get(reverse("provider:add_non_network"))
        self.assertEqual(resp.status_code, 200)

    def test_add_non_network_provider_required_fields(self):
        data = {}
        resp = self.client.post(reverse("provider:add_non_network"), data)
        non_network_fields = self.required_fields
        non_network_fields.remove("is_network")
        provider_errors = {field: self.REQUIRED_ERROR for field in non_network_fields}
        self.check_required_errors(resp, provider_errors)

        detail_errors = {
            field: self.REQUIRED_ERROR for field in self.details_required_fields
        }
        self.assertDictEqual(resp.context["details"].errors, detail_errors)
        self.check_logged_action("tried to create")

    def test_add_non_network_provider_fail_detail_form_validation(self):
        self.erase_logging_file()
        data = self._DATA
        network_1 = base.DataProviderFactory(
            name="test network",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T1").pk],
        )
        network_2 = base.DataProviderFactory(
            name="test network 2",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T2").pk],
        )
        data["networks"] = [network_1.pk, network_2.pk]
        resp = self.client.post(reverse("provider:add_non_network"), data)
        detail_errors = {
            field: self.REQUIRED_ERROR for field in self.details_required_fields
        }
        self.assertDictEqual(resp.context["details"].errors, detail_errors)
        self.check_logged_action("created")

    def test_add_non_network_provider(self):
        self.erase_logging_file()
        data = self._DATA
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        network_1 = base.DataProviderFactory(
            name="test network",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T1").pk],
        )
        network_2 = base.DataProviderFactory(
            name="test network 2",
            is_network=True,
            created_by=self.creator,
            countries=[base.CountryFactory(code="T2").pk],
        )
        data["networks"] = [network_1.pk, network_2.pk]
        resp = self.client.post(reverse("provider:add_non_network"), data)

        provider = models.DataProvider.objects.last()
        details = provider.details.first()
        network_1.refresh_from_db()
        network_2.refresh_from_db()
        data["is_network"] = False

        self.assertEqual(resp.status_code, 302)
        self.check_object(provider, data)

        self.assertEqual(network_1.members.count(), 1)
        self.assertEqual(network_1.members.first(), provider)

        self.assertEqual(network_2.members.count(), 1)
        self.assertEqual(network_2.members.first(), provider)

        self.assertEqual(provider.networks.count(), 2)
        self.assertIn(network_1, provider.networks.all())
        self.assertIn(network_2, provider.networks.all())

        self.assertEqual(provider.details.count(), 1)
        details_data.pop("provider_type")
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, "provider_type").pk, data["provider_type"])
        self.logging()
        self.check_logged_action("created", provider)

    def test_get_edit_non_network_provider(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        resp = self.client.get(
            reverse("provider:edit_non_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_edit_non_network_provider(self):
        self.login_creator()
        self.erase_logging_file()
        data = self._DATA
        data["is_network"] = False
        details_data = self._DETAILS_DATA
        data.update(**details_data)
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        resp = self.client.post(
            reverse("provider:edit_non_network", kwargs={"pk": provider.pk}), data
        )

        self.assertEqual(resp.status_code, 302)
        provider.refresh_from_db()
        data["networks"] = []
        self.check_object(provider, data)
        details.refresh_from_db()
        details_data.pop("provider_type")
        for attr in details_data.keys():
            self.assertEqual(getattr(details, attr), data[attr])
        self.assertEqual(getattr(details, "provider_type").pk, data["provider_type"])
        self.logging()
        self.check_logged_action("updated", provider)

    def test_edit_non_network_provider_fail_detail_form_validation(self):
        self.login_creator()
        self.erase_logging_file()
        data = self._DATA
        data["is_network"] = False
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        resp = self.client.post(
            reverse("provider:edit_non_network", kwargs={"pk": provider.pk}), data
        )
        detail_errors = {
            field: self.REQUIRED_ERROR for field in self.details_required_fields
        }
        self.assertDictEqual(resp.context["details"].errors, detail_errors)
        self.check_logged_action("updated")

    def test_get_edit_network(self):
        self.login_creator()
        self.erase_logging_file()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        response = self.client.get(
            reverse("provider:edit_non_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.logging()

    def test_get_delete_data_provider_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        resp = self.client.get(
            reverse("provider:delete_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(resp.status_code, 200)
        self.logging()

    def test_delete_data_provider_network(self):
        self.login_creator()
        self.erase_logging_file()
        provider = base.DataProviderFactory(is_network=True, created_by=self.creator)
        resp = self.client.post(
            reverse("provider:delete_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProvider)
        self.check_objects_are_soft_deleted(models.DataProvider, DataProviderDoc)
        self.logging()
        self.check_logged_action("deleted", provider)

    def test_delete_data_provider_network_related_objects(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=True, created_by=self.creator)
        data = base.DataFactory(created_by=self.creator)
        base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        base.DataProviderRelationFactory(
            provider=provider, data=data, created_by=self.creator
        )
        self.client.post(
            reverse("provider:delete_network", kwargs={"pk": provider.pk})
        )
        self.check_objects_are_soft_deleted(models.DataProviderDetails)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)
        self.check_logged_action("deleted", provider)

    def test_get_delete_data_provider_non_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        resp = self.client.get(
            reverse("provider:delete_non_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(resp.status_code, 200)

    def test_delete_data_provider_non_network(self):
        self.login_creator()
        self.erase_logging_file()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        resp = self.client.post(
            reverse("provider:delete_non_network", kwargs={"pk": provider.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.DataProvider)
        self.check_objects_are_soft_deleted(models.DataProvider, DataProviderDoc)
        self.logging()
        self.check_logged_action("deleted", provider)

    def test_delete_data_provider_non_network_related_objects(self):
        self.login_creator()
        provider = base.DataProviderFactory(is_network=False, created_by=self.creator)
        data = base.DataFactory(created_by=self.creator)
        base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        base.DataProviderRelationFactory(
            provider=provider, data=data, created_by=self.creator
        )
        self.client.post(
            reverse("provider:delete_non_network", kwargs={"pk": provider.pk})
        )
        self.check_objects_are_soft_deleted(models.DataProviderDetails)
        self.check_objects_are_soft_deleted(models.DataProviderRelation)
        self.check_logged_action("deleted", provider)

    def test_transition_non_network(self):
        self.erase_logging_file()
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=False, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
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
        ]

        for idx, transition in enumerate(transitions):
            for item in items:
                self.assertEqual(getattr(item, "state"), transition["source"])
            self.client.force_login(transition["user"])
            response = self.client.post(
                reverse(
                    "provider:transition",
                    kwargs={
                        "source": transition["source"],
                        "target": transition["target"],
                        "transition": transition["transition"],
                        "pk": provider.pk,
                    },
                )
            )
            self.assertRedirects(
                response, reverse("provider:detail", kwargs={"pk": provider.pk})
            )
            for item in items:
                getattr(item, "refresh_from_db")()
                self.assertEqual(getattr(item, "state"), transition["target"])
            self.check_logged_action(
                "changed state from {source} to {target} for".format(
                    source=transition["source"], target=transition["target"]
                ),
                provider,
                idx + 1,
            )
        self.logging(check_username=False)

    def test_transition_with_draft_data_non_network(self):
        self.erase_logging_file()
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=False, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        for item in items:
            self.assertEqual(getattr(item, "state"), "draft")
        self.client.force_login(self.creator)
        response = self.client.get(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "ready",
                    "transition": "mark_as_ready",
                    "pk": provider.pk,
                },
            )
        )
        self.assertTrue(response.status_code, 200)

    def test_transition_inexistent_state_non_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=False, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        response = self.client.post(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "nosuchstate",
                    "transition": "nosuchtransition",
                    "pk": provider.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, "refresh_from_db")()
            self.assertEqual(getattr(item, "state"), "draft")

    def test_transition_existent_state_no_transition_non_network(self):
        self.login_creator()
        provider = base.DataProviderFactory(
            is_network=False, name="Test provider", created_by=self.creator
        )
        provider_details = base.DataProviderDetailsFactory(
            data_provider=provider, created_by=self.creator
        )
        items = [provider, provider_details]
        response = self.client.post(
            reverse(
                "provider:transition",
                kwargs={
                    "source": "draft",
                    "target": "valid",
                    "transition": "notransition",
                    "pk": provider.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

        for item in items:
            getattr(item, "refresh_from_db")()
            self.assertEqual(getattr(item, "state"), "draft")


class DataProviderPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.redirect_provider_url = reverse("provider:list")
        self.redirect_login_url = reverse("auth:login")

    def test_list_provider_json_non_auth(self):
        resp = self.client.get(reverse("provider:json"))
        self.assertEqual(resp.status_code, 200)

    def test_list_providers_non_auth(self):
        resp = self.client.get(reverse("provider:list"))
        self.assertEqual(resp.status_code, 200)

    def test_detail_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        resp = self.client.get(reverse("provider:detail", kwargs={"pk": provider.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_add_network_provider_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse("provider:add_network"), redirect_url=reverse("provider:list")
        )

    def test_edit_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse("provider:edit_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_edit_network_provider_teammate(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("provider:edit_network", kwargs={"pk": provider.pk}),
        )

    def test_edit_network_provider_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse("provider:edit_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_delete_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse("provider:delete_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_delete_network_provider_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse("provider:delete_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_delete_network_provider_teammate(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("provider:delete_network", kwargs={"pk": provider.pk}),
        )

    def test_add_non_network_provider_non_auth(self):
        self.check_user_redirect_all_methods(
            url=reverse("provider:add_non_network"),
            redirect_url=reverse("provider:list"),
        )

    def test_edit_non_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse("provider:edit_non_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_edit_non_network_provider_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse("provider:edit_non_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_edit_non_network_provider_teammate(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("provider:edit_non_network", kwargs={"pk": provider.pk}),
        )

    def test_delete_non_network_provider_non_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_user_redirect_all_methods(
            url=reverse("provider:delete_non_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_delete_non_network_provider_auth(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_authenticated_user_redirect_all_methods(
            url=reverse("provider:delete_non_network", kwargs={"pk": provider.pk}),
            redirect_url=reverse("provider:list"),
        )

    def test_delete_non_network_provider_teammate(self):
        provider = base.DataProviderFactory(created_by=self.creator)
        self.check_permission_for_teammate(
            method="GET",
            url=reverse("provider:delete_non_network", kwargs={"pk": provider.pk}),
        )
