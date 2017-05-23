# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'countries'


class InspireTheme(models.Model):
    name = models.CharField(max_length=100)
    annex = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class ProductStatus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'product status'


class ProductGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class DefinitionLevel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class TargetDistance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'target distance'


class Relevance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'relevance'


class Criticality(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'criticality'


class Barrier(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class Dissemination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'dissemination'


class Coverage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'coverage'


class Quality(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'quality'


class ComplianceLevel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class Frequency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'frequency'


class Timeliness(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'timeliness'


class Policy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'policy'


class DataType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()


class DataFormat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()
