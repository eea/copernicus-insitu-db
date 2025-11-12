# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.db.models.query import QuerySet
from django_fsm import FSMField, transition
from django.urls import reverse

from markdownx.models import MarkdownxField

from insitu import signals
from copernicus.settings import DATA_DATA_PROVIDER_EDITOR_GROUP
from picklists import models as pickmodels

User = get_user_model()


def user_model_str(self):
    return "{} {}".format(self.first_name, self.last_name)


User.add_to_class("__str__", user_model_str)


def create_team_for_user(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        Team.objects.get(user=instance)
    except ObjectDoesNotExist:
        Team.objects.create(user=instance)


def delete_team_for_user(sender, instance, **kwargs):
    try:
        team = Team.objects.get(user=instance)
        team.delete()
    except ObjectDoesNotExist:
        pass


post_save.connect(create_team_for_user, sender=User)
post_delete.connect(delete_team_for_user, sender=User)


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        for x in self:
            x.delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(_deleted=False)

    def really_all(self):
        return SoftDeleteQuerySet(self.model).all()

    def deleted(self):
        return SoftDeleteQuerySet(self.model).filter(_deleted=True)

    def delete(self):
        self.update(_deleted=True)


class SoftDeleteModel(models.Model):
    _deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    related_objects = []

    class Meta:
        abstract = True

    def delete_related(self):
        for class_name, field in self.related_objects:
            objects = globals()[class_name].objects.filter(**{field: self})
            objects.delete()

    def delete(self, using=None):
        self._deleted = True
        self.save(using=using)
        self.delete_related()
        if hasattr(self, "elastic_delete_signal"):
            self.elastic_delete_signal.send(sender=self)


class OwnerHistoryModel(models.Model):
    owner_history = models.TextField(default="", blank=True)

    class Meta:
        abstract = True

    def set_owner_history(self, user):
        self.owner_history = ";".join(
            [
                "{} {}, ({})".format(user.first_name, user.last_name, user.email),
                self.owner_history,
            ]
        )
        self.save()


class ChangeLog(models.Model):
    version = models.CharField(max_length=10, null=True)
    description = models.TextField(null=True)
    current = models.BooleanField(default=False)
    created_at = models.DateField(null=True)
    updated_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.version


class Release(models.Model):
    version = models.CharField(max_length=50, null=True)
    description = MarkdownxField()
    current = models.BooleanField(default=False)
    created_at = models.DateField(null=True)
    updated_at = models.DateField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "releases"

    def __str__(self):
        return self.version


class LoggedAction(models.Model):
    logged_date = models.DateTimeField(null=True)
    user = models.CharField(max_length=512, null=True)
    action = models.CharField(max_length=512, null=True)
    target_type = models.CharField(max_length=512, null=True)
    id_target = models.CharField(max_length=512, null=True)
    extra = models.CharField(max_length=1024, null=True)
    target_note = models.TextField(blank=True)


def check_owner_user(instance, user):
    """
    Check if the user is the creator or if the user is the creator's
    teammate or if the user has specific permission to edit the object
    (still unsure how the last one applies but we'll leave it there for now)
    """
    result = (
        user == instance.created_by
        or user in instance.created_by.team.teammates.all()
        or instance.has_user_perm(user)
    )
    if type(instance).__name__ == "Data" or type(instance).__name__ == "DataProvider":
        result = (
            result or user.groups.filter(name=DATA_DATA_PROVIDER_EDITOR_GROUP).exists()
        )
    return result


def check_other_user(instance, user):
    """
    Check if the user is different from the  creator or if the is user is
    not in the creator's team
    """
    return (
        user != instance.created_by
        and user not in instance.created_by.team.teammates.all()
        and instance.has_user_perm(user) is not True
    )


class ValidationWorkflowModel(models.Model):
    state = FSMField(default="draft")

    class Meta:
        abstract = True

    @transition(field=state, source="draft", target="ready")
    def mark_as_ready(self):
        pass

    @transition(field=state, source="ready", target="valid")
    def validate(self):
        pass

    @transition(field=state, source="ready", target="draft")
    def cancel(self):
        pass

    @transition(field=state, source="ready", target="changes")
    def request_changes(self):
        pass

    @transition(field=state, source="valid", target="draft")
    def revalidate(self):
        pass

    @transition(field=state, source="changes", target="draft")
    def make_changes(self):
        pass


class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="team")
    teammates = models.ManyToManyField(User, related_name="teams")
    requests = models.ManyToManyField(User, related_name="requests", blank=True)


class Metric(OwnerHistoryModel):
    threshold = models.CharField(max_length=100)
    breakthrough = models.CharField(max_length=100)
    goal = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "T: {} - B: {} - G: {}".format(
            self.threshold, self.breakthrough, self.goal
        )

    def to_elastic_search_format(self):
        return str(self)


class CopernicusService(models.Model):
    acronym = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    website = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class EntrustedEntity(models.Model):
    acronym = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "entrusted entities"

    def __str__(self):
        return self.name


class Component(models.Model):
    acronym = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)
    service = models.ForeignKey(CopernicusService, on_delete=models.CASCADE)
    entrusted_entities = models.ManyToManyField(
        EntrustedEntity, related_name="components", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Requirement(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ("ProductRequirement", "requirement"),
        ("DataRequirement", "requirement"),
    ]
    elastic_delete_signal = signals.requirement_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    dissemination = models.ForeignKey(
        pickmodels.Dissemination, on_delete=models.CASCADE, related_name="+"
    )
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure, on_delete=models.CASCADE, related_name="+"
    )
    group = models.ForeignKey(pickmodels.RequirementGroup, on_delete=models.CASCADE)
    uncertainty = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="+")
    update_frequency = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name="+"
    )
    timeliness = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="+")
    scale = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="+")
    horizontal_resolution = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name="+"
    )
    vertical_resolution = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name="+"
    )
    essential_variables = models.ManyToManyField(
        pickmodels.EssentialVariable,
        blank=True,
    )
    status = models.ForeignKey(
        pickmodels.Status,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    feedback = models.TextField(blank=True)

    owner = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def get_detail_link(self):
        return reverse("requirement:detail", kwargs={"pk": self.id})

    def has_user_perm(self, user):
        return user.has_perm("change_requirement", self) and user.has_perm(
            "delete_requirement", self
        )

    def get_related_objects(self):
        objects = []
        objects += [obj for obj in self.product_requirements.all()]
        objects += [obj for obj in self.datarequirement_set.all()]
        return objects

    @property
    def components(self):
        return Component.objects.filter(products__requirements=self)

    @transition(
        field="state", source="draft", target="ready", permission=check_owner_user
    )
    def mark_as_ready(self):
        for obj in self.get_related_objects():
            if obj.state == "ready":
                continue
            obj.requesting_user = self.requesting_user
            obj.mark_as_ready()
            obj.save()

    @transition(field="state", source="ready", target="valid")
    def validate(self):
        for obj in self.get_related_objects():
            if obj.state == "valid":
                continue
            obj.requesting_user = self.requesting_user
            obj.validate()
            obj.save()

    @transition(
        field="state", source="ready", target="draft", permission=check_owner_user
    )
    def cancel(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.cancel()
            obj.save()

    @transition(
        field="state", source="ready", target="changes", permission=check_other_user
    )
    def request_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "changes":
                continue
            obj.requesting_user = self.requesting_user
            obj.request_changes()
            obj.save()

    @transition(
        field="state", source="valid", target="draft", permission=check_owner_user
    )
    def revalidate(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.revalidate()
            obj.save()

    @transition(
        field="state", source="changes", target="draft", permission=check_owner_user
    )
    def make_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.make_changes()
            obj.save()

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]


class Product(SoftDeleteModel):
    related_objects = [
        ("ProductRequirement", "product"),
    ]
    elastic_delete_signal = signals.product_deleted

    acronym = models.CharField(max_length=75, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    group = models.ForeignKey(pickmodels.ProductGroup, on_delete=models.CASCADE)
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="products"
    )
    status = models.ForeignKey(
        pickmodels.Status, on_delete=models.CASCADE, related_name="+"
    )
    area = models.ForeignKey(
        pickmodels.Area, on_delete=models.CASCADE, related_name="+"
    )
    requirements = models.ManyToManyField(
        Requirement,
        through="ProductRequirement",
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def get_detail_link(self):
        return reverse("product:detail", kwargs={"pk": self.id})

    class Meta:
        indexes = [
            models.Index(fields=["_deleted", "area"]),
        ]


class ProductRequirement(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_requirements"
    )
    requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE, related_name="product_requirements"
    )
    note = models.TextField(blank=True)
    level_of_definition = models.ForeignKey(
        pickmodels.DefinitionLevel, on_delete=models.CASCADE, related_name="+"
    )
    relevance = models.ForeignKey(
        pickmodels.Relevance, on_delete=models.CASCADE, related_name="+"
    )
    criticality = models.ForeignKey(
        pickmodels.Criticality, on_delete=models.CASCADE, related_name="+"
    )
    barriers = models.ManyToManyField(pickmodels.Barrier)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.product.name, self.requirement.name)

    def get_detail_link(self):
        return reverse("requirement:detail", kwargs={"pk": self.requirement.id})

    @property
    def name(self):
        return f"Product: {self.product.name} - Requirement: {self.requirement.name}"

    def has_user_perm(self, user):
        return user.has_perm("change_requirement", self.requirement) and user.has_perm(
            "delete_requirement", self.requirement
        )

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]


class DataProvider(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ("DataProviderDetails", "data_provider"),
        ("DataProviderRelation", "provider"),
    ]
    elastic_delete_signal = signals.data_provider_deleted
    edmo = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    native_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True)
    is_network = models.BooleanField(default=False)
    networks = models.ManyToManyField(
        "self", blank=True, related_name="members", symmetrical=False
    )
    feedback = models.TextField(blank=True)

    countries = models.ManyToManyField(pickmodels.Country)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]

    def __str__(self):
        return self.name

    def get_detail_link(self):
        return reverse("provider:detail", kwargs={"pk": self.id})

    def has_user_perm(self, user):
        return user.has_perm("change_dataprovider", self) and user.has_perm(
            "delete_dataprovider", self
        )

    def get_elastic_search_data(self):
        data = dict()
        details = self.details.first()
        for field in ["acronym", "address", "phone", "email"]:
            data[field] = getattr(details, field) if details else "-"
        data["provider_type"] = (
            getattr(details, "provider_type").name if details else "-"
        )
        data["native_name"] = self.native_name
        return data

    def get_related_objects(self):
        objects = []
        if self.details.all().first() is not None:
            objects = [self.details.all().first()]
        return objects

    @property
    def components(self):
        return Component.objects.filter(
            products__requirements__data__providers=self,
            products__requirements__data__providers___deleted=False,
            products__requirements__data__dataproviderrelation___deleted=False,
            products__requirements__data___deleted=False,
            products__requirements__datarequirement___deleted=False,
            products__requirements___deleted=False,
            products__product_requirements___deleted=False,
            products___deleted=False,
        )

    @transition(
        field="state", source="draft", target="ready", permission=check_owner_user
    )
    def mark_as_ready(self):
        for obj in self.get_related_objects():
            if obj.state == "ready":
                continue
            obj.requesting_user = self.requesting_user
            obj.mark_as_ready()
            obj.save()

    @transition(field="state", source="ready", target="valid")
    def validate(self):
        for obj in self.get_related_objects():
            if obj.state == "valid":
                continue
            obj.requesting_user = self.requesting_user
            obj.validate()
            obj.save()

    @transition(
        field="state", source="ready", target="draft", permission=check_owner_user
    )
    def cancel(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.cancel()
            obj.save()

    @transition(
        field="state", source="ready", target="changes", permission=check_other_user
    )
    def request_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "changes":
                continue
            obj.requesting_user = self.requesting_user
            obj.request_changes()
            obj.save()

    @transition(
        field="state", source="valid", target="draft", permission=check_owner_user
    )
    def revalidate(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.revalidate()
            obj.save()

    @transition(
        field="state", source="changes", target="draft", permission=check_owner_user
    )
    def make_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.make_changes()
            obj.save()


class DataProviderDetails(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    acronym = models.CharField(max_length=10, blank=True)
    website = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    provider_type = models.ForeignKey(
        pickmodels.ProviderType, on_delete=models.CASCADE, related_name="+"
    )
    data_provider = models.ForeignKey(
        DataProvider, on_delete=models.CASCADE, related_name="details"
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "data provider details"
        indexes = [
            models.Index(fields=["_deleted"]),
        ]

    def __str__(self):
        return "Details for {}".format(self.data_provider.name)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        signals.data_provider_updated.send(sender=self)

    def has_user_perm(self, user):
        return user.has_perm(
            "change_dataprovider", self.data_provider
        ) and user.has_perm("delete_dataprovider", self.data_provider)


class Data(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ("DataRequirement", "data"),
        ("DataProviderRelation", "data"),
    ]
    elastic_delete_signal = signals.data_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    update_frequency = models.ForeignKey(
        pickmodels.UpdateFrequency,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    area = models.ForeignKey(
        pickmodels.Area,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    start_time_coverage = models.DateField(null=True, blank=True)
    end_time_coverage = models.DateField(null=True, blank=True)
    timeliness = models.ForeignKey(
        pickmodels.Timeliness,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    data_policy = models.ForeignKey(
        pickmodels.DataPolicy,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="data",
    )
    data_type = models.ForeignKey(
        pickmodels.DataType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    copernicus_service_product = models.BooleanField(default=False)
    data_format = models.ForeignKey(
        pickmodels.DataFormat,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    dissemination = models.ForeignKey(
        pickmodels.Dissemination,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    inspire_themes = models.ManyToManyField(pickmodels.InspireTheme, blank=True)
    status = models.ForeignKey(
        pickmodels.Status,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    geographical_coverage = models.ManyToManyField(pickmodels.Country, blank=True)
    requirements = models.ManyToManyField(Requirement, through="DataRequirement")
    providers = models.ManyToManyField(DataProvider, through="DataProviderRelation")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]

    @property
    def components(self):
        return Component.objects.filter(
            products__requirements__data=self,
            products__requirements___deleted=False,
            products__product_requirements___deleted=False,
            products___deleted=False,
        )

    @property
    def requirements_get_filtered(self):
        return self.requirements.filter(
            datarequirement___deleted=False,
            datarequirement__requirement___deleted=False,
        )

    def __str__(self):
        return self.name

    def get_detail_link(self):
        return reverse("data:detail", kwargs={"pk": self.id})

    def get_related_objects(self):
        objects = []
        objects += [obj for obj in self.dataproviderrelation_set.all()]
        return objects

    @transition(
        field="state", source="draft", target="ready", permission=check_owner_user
    )
    def mark_as_ready(self):
        for obj in self.get_related_objects():
            if obj.state == "ready":
                continue
            obj.requesting_user = self.requesting_user
            obj.mark_as_ready()
            obj.save()

    @transition(field="state", source="ready", target="valid")
    def validate(self):
        for obj in self.get_related_objects():
            if obj.state == "valid":
                continue
            obj.requesting_user = self.requesting_user
            obj.validate()
            obj.save()

    @transition(
        field="state", source="ready", target="draft", permission=check_owner_user
    )
    def cancel(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.cancel()
            obj.save()

    @transition(
        field="state", source="ready", target="changes", permission=check_other_user
    )
    def request_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "changes":
                continue
            obj.requesting_user = self.requesting_user
            obj.request_changes()
            obj.save()

    @transition(
        field="state", source="valid", target="draft", permission=check_owner_user
    )
    def revalidate(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.revalidate()
            obj.save()

    @transition(
        field="state", source="changes", target="draft", permission=check_owner_user
    )
    def make_changes(self):
        for obj in self.get_related_objects():
            if obj.state == "draft":
                continue
            obj.requesting_user = self.requesting_user
            obj.make_changes()
            obj.save()

    def has_user_perm(self, user):
        return user.has_perm("change_data", self) and user.has_perm(
            "delete_data", self
        )


class DataRequirement(OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    information_costs = models.BooleanField(default=False)
    handling_costs = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    level_of_compliance = models.ForeignKey(
        pickmodels.ComplianceLevel, on_delete=models.CASCADE, related_name="+"
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]

    def __str__(self):
        return "{} - {}".format(self.data.name, self.requirement.name)

    def get_detail_link(self):
        return reverse("requirement:detail", kwargs={"pk": self.requirement.id})

    @property
    def name(self):
        return f"Data: {self.data.name} - Requirement: {self.requirement.name}"

    def has_user_perm(self, user):
        return user.has_perm("change_requirement", self.requirement) and user.has_perm(
            "delete_requirement", self.requirement
        )


class DataProviderRelation(
    OwnerHistoryModel, ValidationWorkflowModel, SoftDeleteModel
):
    ORIGINATOR = 1
    DISTRIBUTOR = 2
    ROLE_CHOICES = (
        (ORIGINATOR, "Originator"),
        (DISTRIBUTOR, "Distributor"),
    )
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.data.name, self.provider.name)

    def get_detail_link(self):
        return reverse("data:detail", kwargs={"pk": self.data.id})

    @property
    def name(self):
        return f"Provider: {self.provider.name} - Data: {self.data.name}"

    def has_user_perm(self, user):
        return user.has_perm("change_data", self.data) and user.has_perm(
            "delete_data", self.data
        )

    class Meta:
        indexes = [
            models.Index(fields=["_deleted"]),
        ]


class UserLog(models.Model):
    text = models.CharField(max_length=255)
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
