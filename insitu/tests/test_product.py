import os

from django.core.management import call_command
from django.urls import reverse

from insitu import models
from insitu.documents import ProductDoc
from insitu.tests import base


class ProductTests(base.FormCheckTestCase):
    fields = ["acronym", "name", "note", "description"]
    related_fields = ["group", "component", "status", "area"]
    required_fields = ["name", "group", "component", "status", "area"]
    target_type = "product"

    def setUp(self):
        super().setUp()
        group = base.ProductGroupFactory()
        component = base.ComponentFactory()
        status = base.StatusFactory()
        area = base.AreaFactory()
        self.user = provider_user = base.UserFactory(
            is_superuser=True, username="New user 1"
        )
        self.client.force_login(provider_user)
        self._DATA = {
            "acronym": "TST",
            "name": "TEST product",
            "note": "TEST note",
            "description": "TEST description",
            "group": group.pk,
            "component": component.pk,
            "status": status.pk,
            "area": area.pk,
        }

        with open(os.devnull, "w") as f:
            call_command("search_index", "--rebuild", "-f", stdout=f)

    def test_create_product_fields_required(self):
        data = {}
        resp = self.client.post(reverse("product:add"), data, follow=True)
        self.check_required_errors(resp, self.errors)
        self.check_logged_action("tried to create")

    def test_get_create_product(self):
        resp = self.client.get(reverse("product:add"))
        self.assertEqual(resp.status_code, 200)

    def test_create_product(self):
        data = self._DATA
        resp = self.client.post(reverse("product:add"), data)
        self.assertEqual(resp.status_code, 302)

        obj = self.check_single_object(models.Product, data)
        self.check_logged_action("created", obj)

    def test_list_product_json(self):
        base.ProductFactory()
        resp = self.client.get(reverse("product:json"))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertEqual(data["recordsTotal"], data["recordsFiltered"])

    def test_list_product_json_filter(self):
        base.ProductFactory(name="Test product")
        base.ProductFactory(name="Other product")
        resp = self.client.get(reverse("product:json"), {"search[value]": "Other"})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIsNot(data["recordsTotal"], 0)
        self.assertFalse(data["recordsTotal"] < 2)
        self.assertIs(data["recordsFiltered"], 1)

    def test_list_products(self):
        base.ProductFactory()
        resp = self.client.get(reverse("product:list"))
        self.assertTemplateUsed(resp, "product/list.html")

    def test_detail_product(self):
        product = base.ProductFactory()
        resp = self.client.get(reverse("product:detail", kwargs={"pk": product.pk}))
        self.assertEqual(resp.context["product"], product)

    def test_get_edit_product(self):
        product = base.ProductFactory()
        resp = self.client.get(reverse("product:edit", kwargs={"pk": product.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_edit_product(self):
        product = base.ProductFactory()
        data = self._DATA
        resp = self.client.post(
            reverse("product:edit", kwargs={"pk": product.pk}), data
        )
        self.assertEqual(resp.status_code, 302)
        obj = self.check_single_object(models.Product, data)
        self.check_logged_action("updated", obj)

    def test_entity_and_group_sync_other_filters(self):
        """
        Whenever any of the filters is selected, this should trigger
        a synchronization of all other filters. Because of combinatorial
        explosion it is impractical to test all possible combinations, so this
        only tests one specific case that was selected at random, namely
        `entity`, and `group` triggering the synchronization of `service`,
        `component`, `status` and `area`.
        """
        service_1 = base.CopernicusServiceFactory(name="Service 1")
        service_2 = base.CopernicusServiceFactory(name="Service 2")
        entity_1 = base.EntrustedEntityFactory(acronym="Entity 1")
        entity_2 = base.EntrustedEntityFactory(acronym="Entity 2")

        component_1 = base.ComponentFactory(name="Component 1", service=service_1)
        component_1.entrusted_entities.add(entity_1)
        component_2 = base.ComponentFactory(name="Component 2", service=service_1)
        component_2.entrusted_entities.add(entity_2)
        component_3 = base.ComponentFactory(name="Component 3", service=service_2)
        component_3.entrusted_entities.add(entity_1)

        group_1 = base.ProductGroupFactory(name="Group 1")
        group_2 = base.ProductGroupFactory(name="Group 2")
        status_1 = base.StatusFactory(name="Status 1")
        status_2 = base.StatusFactory(name="Status 2")
        area_1 = base.AreaFactory(name="Area 1")
        area_2 = base.AreaFactory(name="Area 2")

        base.ProductFactory(
            component=component_1, group=group_1, status=status_1, area=area_1
        )
        base.ProductFactory(
            component=component_2, group=group_1, status=status_1, area=area_1
        )
        base.ProductFactory(
            component=component_1, group=group_2, status=status_2, area=area_1
        )
        base.ProductFactory(
            component=component_3, group=group_1, status=status_1, area=area_2
        )

        resp = self.client.get(
            reverse("product:json"),
            {"entity": entity_1.acronym, "group": group_1.name},
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.json()

        filters = {
            "component": {"options": ["Component 1", "Component 3"], "selected": None},
            "area": {"options": ["Area 1", "Area 2"], "selected": None},
            "entity": {"options": ["Entity 1"], "selected": "Entity 1"},
            "group": {"options": ["Group 1"], "selected": "Group 1"},
            "service": {"options": ["Service 1", "Service 2"], "selected": None},
            "status": {"options": ["Status 1"], "selected": None},
        }

        self.assertEqual(data["filters"], filters)

    def test_get_delete_product(self):
        product = base.ProductFactory()
        resp = self.client.get(reverse("product:delete", kwargs={"pk": product.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_delete_product(self):
        product = base.ProductFactory()
        resp = self.client.post(reverse("product:delete", kwargs={"pk": product.pk}))
        self.assertEqual(resp.status_code, 302)
        self.check_logged_action("deleted", product)
        self.check_single_object_deleted(models.Product)
        self.check_objects_are_soft_deleted(models.Product, ProductDoc)

    def test_delete_product_related_objects(self):
        product = base.ProductFactory()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        base.ProductRequirementFactory(
            product=product, requirement=requirement, created_by=self.creator
        )
        self.client.post(reverse("product:delete", kwargs={"pk": product.pk}))
        self.check_logged_action("deleted", product)
        self.check_objects_are_soft_deleted(models.ProductRequirement)


class ProductPermissionTests(base.PermissionsCheckTestCase):
    def setUp(self):
        self.redirect_url = reverse("product:list")
        self.methods = ["GET", "POST"]

    def test_list_product_json_non_auth(self):
        resp = self.client.get(reverse("product:json"))
        self.assertEqual(resp.status_code, 200)

    def test_product_list_not_auth(self):
        resp = self.client.get(reverse("product:list"))
        self.assertEqual(resp.status_code, 200)

    def test_product_detail_not_auth(self):
        product = base.ProductFactory()
        resp = self.client.get(reverse("product:detail", kwargs={"pk": product.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_product_add_not_auth(self):
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url, url=reverse("product:add")
        )

    def test_product_edit_not_auth(self):
        product = base.ProductFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("product:edit", kwargs={"pk": product.pk}),
        )

    def test_product_delete_not_auth(self):
        product = base.ProductFactory()
        self.check_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("product:delete", kwargs={"pk": product.pk}),
        )

    def test_product_relation_add_auth(self):
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_url, url=reverse("product:add")
        )

    def test_product_relation_edit_auth(self):
        product = base.ProductFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("product:edit", kwargs={"pk": product.pk}),
        )

    def test_product_relation_delete_auth(self):
        product = base.ProductFactory()
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=self.redirect_url,
            url=reverse("product:delete", kwargs={"pk": product.pk}),
        )
