# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SortedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("sort_order")


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class InspireTheme(models.Model):
    name = models.CharField(max_length=100)
    annex = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return "{}: {}".format(self.annex, self.name) if self.annex else self.name


class EssentialVariable(models.Model):
    domain = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    parameter = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return "{} - {} - {}".format(self.domain, self.component, self.parameter)


class Status(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=300, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "status"

    def __str__(self):
        return self.name


class ProductGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class RequirementGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class DefinitionLevel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Relevance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "relevance"

    def __str__(self):
        return self.name


class Criticality(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "criticality"

    def __str__(self):
        return self.name


class Barrier(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Dissemination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "dissemination"

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "areas"

    def __str__(self):
        return self.name


class QualityControlProcedure(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "quality_control_procedure"

    def __str__(self):
        return self.name


class ComplianceLevel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class UpdateFrequency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "update frequency"

    def __str__(self):
        return self.name


class Timeliness(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "timeliness"

    def __str__(self):
        return self.name


class DataPolicy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "Data policies"

    def __str__(self):
        return self.name


class DataType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class DataFormat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class ProviderType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
    link = models.CharField(max_length=100, blank=True)

    objects = SortedManager()

    def __str__(self):
        return self.name
