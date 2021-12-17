import copy

from django.urls import reverse

from insitu import models
from insitu.tests import base

REQUIRED_ERROR = ["This field is required."]


class ProductRequirementTests(base.FormCheckTestCase):
    fields = ["note"]
    related_fields = [
        "requirement",
        "product",
        "level_of_definition",
        "relevance",
        "criticality",
    ]
    many_to_many_fields = ["barriers"]
    required_fields = [
        "requirement",
        "product",
        "level_of_definition",
        "relevance",
        "criticality",
        "barriers",
    ]

    def setUp(self):
        super().setUp()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        self.requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        self.product = base.ProductFactory()
        level_of_definition = base.DefinitionLevelFactory()
        self.relevance = base.RelevanceFactory()
        criticality = base.CriticalityFactory()
        barriers = [base.BarrierFactory(), base.BarrierFactory()]

        self._DATA = {
            "note": "test note",
            "requirement": self.requirement.pk,
            "product": self.product.pk,
            "level_of_definition": level_of_definition.pk,
            "relevance": self.relevance.pk,
            "criticality": criticality.pk,
            "barriers": [barrier.pk for barrier in barriers],
        }
        user = base.UserFactory(username="User ProductRequirement")
        self.client.force_login(user)

    def test_product_requirement_add_required_fields(self):
        data = {}
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        errors_requirement = self.errors.copy()
        errors_requirement.pop("requirement")

        resp = self.client.post(
            reverse(
                "requirement:product:add", kwargs={"requirement_pk": requirement.pk}
            ),
            data,
        )
        self.check_required_errors(resp, errors_requirement)

    def test_get_product_requirement_add(self):
        resp = self.client.get(
            reverse(
                "requirement:product:add",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_product_requirement_add(self):
        data = self._DATA
        resp = self.client.post(
            reverse(
                "requirement:product:add",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_add_unique(self):
        base.ProductRequirementFactory(
            product=self.product,
            requirement=self.requirement,
            relevance=self.relevance,
            created_by=self.creator,
        )
        data = self._DATA
        resp = self.client.post(
            reverse(
                "requirement:product:add",
                kwargs={"requirement_pk": self.requirement.pk},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["form"].errors, {"__all__": ["This relation already exists."]}
        )

    def test_get_product_requirement_edit(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        resp = self.client.get(
            reverse(
                "requirement:product:edit",
                kwargs={
                    "requirement_pk": product_requirement.requirement.pk,
                    "pk": product_requirement.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_product_requirement_edit(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        data = self._DATA
        data["product"] = product_requirement.product.id
        data["requirement"] = product_requirement.requirement.id
        data["relevance"] = product_requirement.relevance.id

        resp = self.client.post(
            reverse(
                "requirement:product:edit",
                kwargs={
                    "requirement_pk": product_requirement.requirement.pk,
                    "pk": product_requirement.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        data["product"] = product_requirement.product.pk
        data["requirement"] = product_requirement.requirement.pk
        self.check_single_object(models.ProductRequirement, data)

    def test_product_requirement_edit_unique(self):
        self.login_creator()
        self.product_two = base.ProductFactory()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            product=self.product,
            requirement=requirement,
            created_by=self.creator,
            relevance=self.relevance,
        )
        base.ProductRequirementFactory(
            requirement=requirement,
            product=self.product_two,
            created_by=self.creator,
            relevance=self.relevance,
        )
        data = self._DATA
        data["product"] = self.product_two.id
        data["requirement"] = product_requirement.requirement.id
        data["relevance"] = product_requirement.relevance.id

        resp = self.client.post(
            reverse(
                "requirement:product:edit",
                kwargs={
                    "requirement_pk": product_requirement.requirement.pk,
                    "pk": product_requirement.pk,
                },
            ),
            data,
        )
        data = self._DATA
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["form"].errors, {"__all__": ["This relation already exists."]}
        )

    def test_get_product_requirement_delete(self):
        self.login_creator()
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        resp = self.client.get(
            reverse(
                "requirement:product:delete",
                kwargs={
                    "requirement_pk": product_requirement.requirement.pk,
                    "pk": product_requirement.pk,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_product_requirement_delete(self):
        self.login_creator()
        data = {}
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        resp = self.client.post(
            reverse(
                "requirement:product:delete",
                kwargs={
                    "requirement_pk": product_requirement.requirement.pk,
                    "pk": product_requirement.pk,
                },
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object_deleted(models.ProductRequirement)

    def test_product_group_requirement_add_required_fields(self):
        data = {}
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        errors_requirement = self.errors.copy()
        errors_requirement.pop("requirement")
        errors_requirement.pop("product")
        errors_requirement["product_group"] = ["This field is required."]

        resp = self.client.post(
            reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": requirement.pk},
            ),
            data,
        )
        self.check_required_errors(resp, errors_requirement)

    def test_product_group_requirement_add(self):
        data = copy.deepcopy(self._DATA)
        data.pop("product")
        product_group = base.ProductGroupFactory()
        data["product_group"] = product_group.pk
        resp = self.client.post(
            reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        self.check_single_object(models.ProductRequirement, self._DATA)

    def test_product_group_requirement_add_unique_relation_raise_error(self):
        data = copy.deepcopy(self._DATA)
        data.pop("product")
        product_group = base.ProductGroupFactory()
        data["product_group"] = product_group.pk
        self.client.post(
            reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        resp = self.client.post(
            reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 200)
        unique_relation_error = {
            "__all__": ["A relation already exists for all products of this group."]
        }
        self.assertEqual(resp.context["form"].errors, unique_relation_error)

    def test_product_group_requirement_add_unique_relation_to_products_without(self):
        data = copy.deepcopy(self._DATA)
        data.pop("product")
        product_group = base.ProductGroupFactory()
        product1 = base.ProductFactory(group=product_group)
        product2 = base.ProductFactory(group=product_group)
        base.ProductRequirementFactory(
            product=product1,
            requirement=self.requirement,
            relevance=self.relevance,
            created_by=self.creator,
        )
        data["product_group"] = product_group.pk
        resp = self.client.post(
            reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": self._DATA["requirement"]},
            ),
            data,
        )
        self.assertEqual(resp.status_code, 302)
        products = [
            product_requirement.product
            for product_requirement in models.ProductRequirement.objects.filter(
                product__group=product_group
            )
        ]
        self.assertEqual(len(products), 2)
        self.assertIn(product1, products)
        self.assertIn(product2, products)


class ProductRequirementPermissionsTests(base.PermissionsCheckTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse("auth:login")

    def test_product_requirement_add_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:add", kwargs={"requirement_pk": requirement.pk}
            ),
        )

    def test_product_group_requirement_add_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:add_group",
                kwargs={"requirement_pk": requirement.pk},
            ),
        )

    def test_product_requirement_edit_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:edit",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )

    def test_product_requirement_edit_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:edit",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )

    def test_product_requirement_edit_teammate(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "requirement:product:edit",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )

    def test_product_requirement_delete_not_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:delete",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )

    def test_product_requirement_delete_auth(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_authenticated_user_redirect_all_methods(
            redirect_url=reverse("requirement:list"),
            url=reverse(
                "requirement:product:delete",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )

    def test_product_requirement_delete_teammate(self):
        metrics = base.RequirementFactory.create_metrics(self.creator)
        requirement = base.RequirementFactory(created_by=self.creator, **metrics)
        product_requirement = base.ProductRequirementFactory(
            requirement=requirement, created_by=self.creator
        )
        self.check_permission_for_teammate(
            method="GET",
            url=reverse(
                "requirement:product:delete",
                kwargs={"requirement_pk": requirement.pk, "pk": product_requirement.pk},
            ),
        )
