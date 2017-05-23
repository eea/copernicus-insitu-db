# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

from picklists import models as picklists


class Metric(models.Model):
    threshold = models.CharField(max_length=100)
    breakthrough = models.CharField(max_length=100)
    goal = models.CharField(max_length=100)


class CopernicusService(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField()
    website = models.CharField(max_length=255)


class EntrustedEntity(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'entrusted entities'


class Component(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    service = models.ForeignKey(CopernicusService, on_delete=models.CASCADE)
    entrusted_entity = models.ForeignKey(EntrustedEntity,
                                         on_delete=models.CASCADE)


class Requirement(models.Model):
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    dissemination = models.ForeignKey(picklists.Dissemination,
                                      on_delete=models.CASCADE,
                                      related_name='+')
    quality = models.ForeignKey(picklists.Quality,
                                on_delete=models.CASCADE,
                                related_name='+')
    uncertainty = models.ForeignKey(Metric,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    frequency = models.ForeignKey(Metric,
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


class Product(models.Model):
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    group = models.ForeignKey(picklists.ProductGroup,
                              on_delete=models.CASCADE)
    component = models.ForeignKey(Component,
                                  on_delete=models.CASCADE)
    status = models.ForeignKey(picklists.ProductStatus,
                               on_delete=models.CASCADE,
                               related_name='+')
    coverage = models.ForeignKey(picklists.Coverage,
                                 on_delete=models.CASCADE,
                                 related_name='+')
    requirements = models.ManyToManyField(Requirement,
                                          through='ProductRequirement')


class ProductRequirement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    level_of_definition = models.ForeignKey(picklists.DefinitionLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')
    distance_to_target = models.ForeignKey(picklists.TargetDistance,
                                           on_delete=models.CASCADE,
                                           related_name='+')
    relevance = models.ForeignKey(picklists.Relevance,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    criticality = models.ForeignKey(picklists.Criticality,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    barriers = models.ManyToManyField(picklists.Barrier)


class DataResponsible(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_network = models.BooleanField(default=False)
    members = models.ManyToManyField('self', blank=True)
    countries = models.ManyToManyField(picklists.Country)


class DataResponsibleDetails(models.Model):
    COMMERCIAL = 1
    PUBLIC = 2
    INSTITUTIONAL = 3
    TYPE_CHOICES = (
        (COMMERCIAL, 'Commercial'),
        (PUBLIC, 'Public'),
        (INSTITUTIONAL, 'Institutional'),
    )
    acronym = models.CharField(max_length=10)
    website = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    responsible_type = models.IntegerField(choices=TYPE_CHOICES, db_index=True)
    data_responsible = models.ForeignKey(DataResponsible,
                                         on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'data responsible details'


class DataGroup(models.Model):
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    frequency = models.ForeignKey(picklists.Frequency,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    coverage = models.ForeignKey(picklists.Coverage,
                                 on_delete=models.CASCADE,
                                 related_name='+')
    timeliness = models.ForeignKey(picklists.Timeliness,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    policy = models.ForeignKey(picklists.Policy,
                               on_delete=models.CASCADE,
                               related_name='+')
    data_type = models.ForeignKey(picklists.DataType,
                                  on_delete=models.CASCADE,
                                  related_name='+')
    data_format = models.ForeignKey(picklists.DataFormat,
                                    on_delete=models.CASCADE,
                                    related_name='+')
    quality = models.ForeignKey(picklists.Quality,
                                on_delete=models.CASCADE,
                                related_name='+')
    inspire_themes = models.ManyToManyField(picklists.InspireTheme)
    requirements = models.ManyToManyField(Requirement,
                                          through='DataRequirement')
    responsibles = models.ManyToManyField(DataResponsible,
                                          through='DataResponsibleRelation')


class DataRequirement(models.Model):
    data_group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    information_costs = models.BooleanField(default=False)
    handling_costs = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    level_of_compliance = models.ForeignKey(picklists.ComplianceLevel,
                                            on_delete=models.CASCADE,
                                            related_name='+')


class DataResponsibleRelation(models.Model):
    ORIGINATOR = 1
    DISTRIBUTOR = 2
    ROLE_CHOICES = (
        (ORIGINATOR, 'Originator'),
        (DISTRIBUTOR, 'Distributor'),
    )
    data_group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    responsible = models.ForeignKey(DataResponsible, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, db_index=True)
