# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet

from insitu import signals
from picklists import models as pickmodels


User = get_user_model()


class _WithRelatedUserManager(models.Manager):
    """
    A manager whose default queryset pre-selects the related user object
    for performance reasons.
    """

    def get_queryset(self):
        return super().get_queryset().select_related('user')


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


class Metric(models.Model):
    threshold = models.CharField(max_length=100)
    breakthrough = models.CharField(max_length=100)
    goal = models.CharField(max_length=100)
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
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    website = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


class EntrustedEntity(models.Model):
    acronym = models.CharField(max_length=10, blank=True)
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
    name = models.CharField(max_length=100)
    service = models.ForeignKey(CopernicusService, on_delete=models.CASCADE)
    entrusted_entity = models.ForeignKey(EntrustedEntity,
                                         on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


class Requirement(SoftDeleteModel):
    related_objects = [
        ('ProductRequirement', 'requirement'),
        ('DataRequirement', 'requirement')
    ]
    elastic_delete_signal = signals.requirement_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    dissemination = models.ForeignKey(pickmodels.Dissemination,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure,
        on_delete=models.CASCADE,
        related_name='+'
    )
    group = models.ForeignKey(pickmodels.RequirementGroup,
                              on_delete=models.CASCADE)
    uncertainty = models.ForeignKey(Metric,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    update_frequency = models.ForeignKey(Metric,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    timeliness = models.ForeignKey(Metric,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    horizontal_resolution = models.ForeignKey(Metric,
                                              on_delete=models.CASCADE,
                                              related_name='+')
    vertical_resolution = models.ForeignKey(Metric,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return self.name


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
    coverage = models.ForeignKey(pickmodels.Coverage,
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


class ProductRequirement(SoftDeleteModel):
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
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.requirement.name)


class DataResponsible(SoftDeleteModel):
    related_objects = [
        ('DataResponsibleDetails', 'data_responsible'),
        ('DataResponsibleRelation', 'responsible'),
    ]
    elastic_delete_signal = signals.data_responsible_deleted

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_network = models.BooleanField(default=False)
    networks = models.ManyToManyField('self', blank=True,
                                      related_name='members',
                                      symmetrical=False)
    countries = models.ManyToManyField(pickmodels.Country)
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
        data['responsible_type'] = (
            getattr(details, 'responsible_type').name if details else '-'
        )
        return data


class DataResponsibleDetails(SoftDeleteModel):
    acronym = models.CharField(max_length=10, blank=True)
    website = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    responsible_type = models.ForeignKey(pickmodels.ResponsibleType,
                                         on_delete=models.CASCADE,
                                         related_name='+')
    data_responsible = models.ForeignKey(DataResponsible,
                                         on_delete=models.CASCADE,
                                         related_name='details')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    class Meta:
        verbose_name_plural = 'data responsible details'

    def __str__(self):
        return 'Details for {}'.format(self.data_responsible.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        signals.data_resposible_updated.send(sender=self)


class Data(SoftDeleteModel):
    related_objects = [
        ('DataRequirement', 'data'),
        ('DataResponsibleRelation', 'data'),
    ]
    elastic_delete_signal = signals.data_deleted

    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    update_frequency = models.ForeignKey(pickmodels.UpdateFrequency,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    coverage = models.ForeignKey(pickmodels.Coverage,
                                 on_delete=models.CASCADE,
                                 related_name='+')
    start_time_coverage = models.DateField(null=True)
    end_time_coverage = models.DateField(null=True)
    timeliness = models.ForeignKey(pickmodels.Timeliness,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    policy = models.ForeignKey(pickmodels.Policy,
                               on_delete=models.CASCADE,
                               related_name='+')
    data_type = models.ForeignKey(pickmodels.DataType,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    data_format = models.ForeignKey(pickmodels.DataFormat,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    quality_control_procedure = models.ForeignKey(
        pickmodels.QualityControlProcedure,
        on_delete=models.CASCADE,
        related_name='+'
    )
    dissemination = models.ForeignKey(pickmodels.Dissemination,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    inspire_themes = models.ManyToManyField(pickmodels.InspireTheme)
    essential_variables = models.ManyToManyField(
        pickmodels.EssentialVariable
    )
    requirements = models.ManyToManyField(Requirement,
                                          through='DataRequirement')
    responsibles = models.ManyToManyField(DataResponsible,
                                          through='DataResponsibleRelation')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)


    def __str__(self):
        return self.name


class DataRequirement(SoftDeleteModel):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    information_costs = models.BooleanField(default=False)
    handling_costs = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    level_of_compliance = models.ForeignKey(pickmodels.ComplianceLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.data.name, self.requirement.name)


class DataResponsibleRelation(SoftDeleteModel):
    ORIGINATOR = 1
    DISTRIBUTOR = 2
    ROLE_CHOICES = (
        (ORIGINATOR, 'Originator'),
        (DISTRIBUTOR, 'Distributor'),
    )
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    responsible = models.ForeignKey(DataResponsible, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)

    def __str__(self):
        return '{} - {}'.format(self.data.name, self.responsible.name)


class CopernicusResponsibleManager(_WithRelatedUserManager):
    pass


class CopernicusResponsible(models.Model):
    user = models.OneToOneField(User,
                                related_name='service_resp')
    service = models.ForeignKey(CopernicusService,
                                related_name='responsible')

    objects = CopernicusResponsibleManager()
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)


class CountryResponsibleManager(_WithRelatedUserManager):
    pass


class CountryResponsible(models.Model):
    user = models.OneToOneField(User,
                                related_name='country_resp')
    country = models.ForeignKey(pickmodels.Country,
                                related_name='responsible')

    objects = CountryResponsibleManager()
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)


class DataProviderManager(_WithRelatedUserManager):
    pass


class DataProvider(models.Model):
    user = models.OneToOneField(User,
                                related_name='data_resp')
    responsible = models.ForeignKey(DataResponsible,
                                    related_name='responsible')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True)
