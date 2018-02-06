# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet
from django_xworkflows.models import Workflow, WorkflowEnabled, StateField
from xworkflows import (
    transition_check, transition,
    ForbiddenTransition,
)

from insitu import signals
from picklists import models as pickmodels

User = get_user_model()


class ValidationWorkflow(Workflow):
    name = 'validation'

    states = (
        # name, title
        ('draft', 'Draft'),
        ('ready', 'Ready for validation'),
        ('valid', 'Valid'),
        ('changes', 'Changes requested')
    )

    initial_state = 'draft'

    transitions = (
        # name, source state, target state
        ('mark_as_ready', 'draft', 'ready'),
        ('validate', 'ready', 'valid'),
        ('cancel', 'ready', 'draft'),
        ('request_changes', 'ready', 'changes'),
        ('make_changes', 'changes', 'draft')
    )

    @classmethod
    def __check_state_exists(cls, state):
        if state not in cls.states:
            raise ForbiddenTransition()

    @classmethod
    def __check_transition_between_states_exist(cls, source_state, target_state):
        for trans in cls.transitions:
            for source in trans.source:
                if (source.name == source_state and
                        trans.target.name == target_state):
                    return
        raise ForbiddenTransition()

    @classmethod
    def check_transition(cls, source_state, target_state):
        cls.__check_state_exists(source_state)
        cls.__check_state_exists(target_state)
        cls.__check_transition_between_states_exist(source_state, target_state)

    @classmethod
    def get_transition(cls, source_state, target_state):
        cls.check_transition(source_state, target_state)
        for trans in cls.transitions:
            for source in trans.source:
                if (source.name == source_state and
                        trans.target.name == target_state):
                    return trans.name
        raise ForbiddenTransition()


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

    def delete_related(self):
        for class_name, field in self.related_objects:
            objects = globals()[class_name].objects.filter(
                **{field: self})
            objects.delete()

    def delete(self, using=None):
        self._deleted = True
        self.save(using=using)
        self.delete_related()
        if hasattr(self, 'elastic_delete_signal'):
            self.elastic_delete_signal.send(sender=self)

    class Meta:
        abstract = True


class ValidationWorkflowModel(WorkflowEnabled, models.Model):
    state = StateField(ValidationWorkflow)

    class Meta:
        abstract = True

    @transition()
    def mark_as_ready(self):
        pass

    @transition()
    def validate(self):
        pass

    @transition()
    def cancel(self):
        pass

    @transition()
    def request_changes(self):
        pass

    @transition()
    def make_changes(self):
        pass

    @transition_check('mark_as_ready', 'cancel', 'make_changes')
    def check_owner_user(self, *args, **kwargs):
        return self.requesting_user == self.created_by

    @transition_check('validate', 'request_changes')
    def check_other_user(self, *args, **kwargs):
        return self.requesting_user != self.created_by


class Metric(ValidationWorkflowModel):
    threshold = models.CharField(max_length=100)
    breakthrough = models.CharField(max_length=100)
    goal = models.CharField(max_length=100)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return 'T: {} - B: {} - G: {}'.format(
            self.threshold, self.breakthrough, self.goal)

    def to_elastic_search_format(self):
        return str(self)


class CopernicusService(models.Model):
    acronym = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True)
    website = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


class EntrustedEntity(models.Model):
    acronym = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    class Meta:
        verbose_name_plural = 'entrusted entities'

    def __str__(self):
        return self.name


class Component(models.Model):
    acronym = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100, unique=True)
    service = models.ForeignKey(CopernicusService, on_delete=models.CASCADE)
    entrusted_entity = models.ForeignKey(
        EntrustedEntity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Requirement(ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ('ProductRequirement', 'requirement'),
        ('DataRequirement', 'requirement')
    ]
    elastic_delete_signal = signals.requirement_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    dissemination = models.ForeignKey(
        pickmodels.Dissemination, on_delete=models.CASCADE, related_name='+')
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure,
        on_delete=models.CASCADE,
        related_name='+'
    )
    group = models.ForeignKey(
        pickmodels.RequirementGroup, on_delete=models.CASCADE)
    uncertainty = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name='+')
    update_frequency = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name='+')
    timeliness = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name='+')
    horizontal_resolution = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name='+')
    vertical_resolution = models.ForeignKey(
        Metric, on_delete=models.CASCADE, related_name='+')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def get_related_objects(self):
        metrics = ['uncertainty', 'update_frequency', 'timeliness',
                   'horizontal_resolution', 'vertical_resolution']
        objects = [getattr(self, metric) for metric in metrics]

        objects += [obj for obj in self.productrequirement_set.all()]
        objects += [obj for obj in self.datarequirement_set.all()]
        objects += [obj for obj in self.data_set.distinct().all()]
        objects += [obj for obj in DataProviderRelation.objects.filter(
            data__requirements=self).distinct()]
        objects += [obj for obj in DataProvider.objects.filter(
            data__requirements=self).distinct()]
        objects += [obj for obj in DataProviderDetails.objects.filter(
            data_provider__data__requirements=self).distinct()]
        return objects

    @transition()
    def mark_as_ready(self):
        for obj in self.get_related_objects():
            obj.requesting_user = self.requesting_user
            obj.mark_as_ready()

    @transition()
    def validate(self):
        for obj in self.get_related_objects():
            obj.requesting_user = self.requesting_user
            obj.validate()

    @transition()
    def cancel(self):
        for obj in self.get_related_objects():
            obj.requesting_user = self.requesting_user
            obj.cancel()

    @transition()
    def request_changes(self):
        for obj in self.get_related_objects():
            obj.requesting_user = self.requesting_user
            obj.request_changes()

    @transition()
    def make_changes(self):
        for obj in self.get_related_objects():
            obj.requesting_user = self.requesting_user
            obj.make_changes()


class Product(SoftDeleteModel):
    related_objects = [
        ('ProductRequirement', 'product'),
    ]
    elastic_delete_signal = signals.product_deleted

    acronym = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    group = models.ForeignKey(pickmodels.ProductGroup,
                              on_delete=models.CASCADE)
    component = models.ForeignKey(Component,
                                  on_delete=models.CASCADE)
    status = models.ForeignKey(pickmodels.ProductStatus,
                               on_delete=models.CASCADE,
                               related_name='+')
    area = models.ForeignKey(pickmodels.Area,
                             on_delete=models.CASCADE,
                             related_name='+')
    requirements = models.ManyToManyField(Requirement,
                                          through='ProductRequirement')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


class ProductRequirement(ValidationWorkflowModel, SoftDeleteModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    level_of_definition = models.ForeignKey(pickmodels.DefinitionLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    relevance = models.ForeignKey(pickmodels.Relevance,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    criticality = models.ForeignKey(pickmodels.Criticality,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    barriers = models.ManyToManyField(pickmodels.Barrier)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.requirement.name)


class DataProvider(ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ('DataProviderDetails', 'data_provider'),
        ('DataProviderRelation', 'provider'),
    ]
    elastic_delete_signal = signals.data_provider_deleted

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_network = models.BooleanField(default=False)
    networks = models.ManyToManyField('self', blank=True,
                                      related_name='members',
                                      symmetrical=False)
    countries = models.ManyToManyField(pickmodels.Country)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name

    def get_elastic_search_data(self):
        data = dict()
        details = self.details.first()
        for field in ['acronym', 'address', 'phone', 'email', 'contact_person']:
            data[field] = getattr(details, field) if details else '-'
        data['provider_type'] = (
            getattr(details, 'provider_type').name if details else '-'
        )
        return data


class DataProviderDetails(ValidationWorkflowModel, SoftDeleteModel):
    acronym = models.CharField(max_length=10, blank=True)
    website = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    provider_type = models.ForeignKey(pickmodels.ProviderType,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    data_provider = models.ForeignKey(DataProvider,
                                      on_delete=models.CASCADE,
                                      related_name='details')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    class Meta:
        verbose_name_plural = 'data provider details'

    def __str__(self):
        return 'Details for {}'.format(self.data_provider.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        signals.data_provider_updated.send(sender=self)


class Data(ValidationWorkflowModel, SoftDeleteModel):
    related_objects = [
        ('DataRequirement', 'data'),
        ('DataProviderRelation', 'data'),
    ]
    elastic_delete_signal = signals.data_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    update_frequency = models.ForeignKey(pickmodels.UpdateFrequency,
                                         null=True, blank=True,
                                         on_delete=models.CASCADE,
                                         related_name='+')
    area = models.ForeignKey(pickmodels.Area,
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name='+')
    start_time_coverage = models.DateField(null=True, blank=True)
    end_time_coverage = models.DateField(null=True, blank=True)
    timeliness = models.ForeignKey(pickmodels.Timeliness,
                                   null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    data_policy = models.ForeignKey(pickmodels.DataPolicy,
                                    null=True, blank=True,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    data_type = models.ForeignKey(pickmodels.DataType,
                                  null=True, blank=True,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    data_format = models.ForeignKey(pickmodels.DataFormat,
                                    null=True, blank=True,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    dissemination = models.ForeignKey(pickmodels.Dissemination,
                                      null=True, blank=True,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    inspire_themes = models.ManyToManyField(pickmodels.InspireTheme,
                                            blank=True)
    essential_variables = models.ManyToManyField(
        pickmodels.EssentialVariable,
        blank=True,
    )
    requirements = models.ManyToManyField(Requirement,
                                          through='DataRequirement')
    providers = models.ManyToManyField(DataProvider,
                                       through='DataProviderRelation')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


class DataRequirement(ValidationWorkflowModel, SoftDeleteModel):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    information_costs = models.BooleanField(default=False)
    handling_costs = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    level_of_compliance = models.ForeignKey(pickmodels.ComplianceLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.data.name, self.requirement.name)


class DataProviderRelation(ValidationWorkflowModel, SoftDeleteModel):
    ORIGINATOR = 1
    DISTRIBUTOR = 2
    ROLE_CHOICES = (
        (ORIGINATOR, 'Originator'),
        (DISTRIBUTOR, 'Distributor'),
    )
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, db_index=True)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.data.name, self.provider.name)
