# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from picklists import models

class AreaAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class BarriersAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order')


class ComplianceLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']
    list_display = ('code', 'name')


class CriticalityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class DataFormatAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class DataPolicyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class DataTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class DefinitionLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class DisseminationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'description', 'sort_order', 'link')


class EssentialVariableAdmin(admin.ModelAdmin):
    search_fields = ['domain','component', 'parameter']
    list_display = ['domain', 'component', 'parameter', 'description', 'sort_order', 'link']


class InspireThemeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'annex']
    list_display = ['name', 'annex', 'description', 'sort_order', 'link']


class ProductGroupAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order']


class ProductStatusAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


class ProviderTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


class QualityControlProcedureAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


class RelevanceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


class RequirementGroupAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order']


class TimelinessAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


class UpdateFrequencyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'description', 'sort_order', 'link']


admin.site.register(models.Area, AreaAdmin)
admin.site.register(models.Barrier, BarriersAdmin)
admin.site.register(models.ComplianceLevel, ComplianceLevelAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.Criticality, CriticalityAdmin)
admin.site.register(models.DataFormat, DataFormatAdmin)
admin.site.register(models.DataPolicy, DataPolicyAdmin)
admin.site.register(models.DataType, DataTypeAdmin)
admin.site.register(models.DefinitionLevel, DefinitionLevelAdmin)
admin.site.register(models.Dissemination, DisseminationAdmin)
admin.site.register(models.EssentialVariable, EssentialVariableAdmin)
admin.site.register(models.InspireTheme, InspireThemeAdmin)
admin.site.register(models.ProductGroup, ProductGroupAdmin)
admin.site.register(models.ProductStatus, ProductStatusAdmin)
admin.site.register(models.ProviderType, ProviderTypeAdmin)
admin.site.register(models.QualityControlProcedure, QualityControlProcedureAdmin)
admin.site.register(models.Relevance, RelevanceAdmin)
admin.site.register(models.RequirementGroup, RequirementGroupAdmin)
admin.site.register(models.Timeliness, TimelinessAdmin)
admin.site.register(models.UpdateFrequency, UpdateFrequencyAdmin)
