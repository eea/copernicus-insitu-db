# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from picklists import models


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name']

class InspireThemeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'annex']


class EssentialVariableAdmin(admin.ModelAdmin):
    search_fields = ['parameter']


admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.InspireTheme, InspireThemeAdmin)
admin.site.register(models.EssentialVariable, EssentialVariableAdmin)
admin.site.register(models.ProductStatus)
admin.site.register(models.ProductGroup)
admin.site.register(models.RequirementGroup)
admin.site.register(models.DefinitionLevel)
admin.site.register(models.Relevance)
admin.site.register(models.Criticality)
admin.site.register(models.Barrier)
admin.site.register(models.Dissemination)
admin.site.register(models.Coverage)
admin.site.register(models.QualityControlProcedure)
admin.site.register(models.ComplianceLevel)
admin.site.register(models.UpdateFrequency)
admin.site.register(models.Timeliness)
admin.site.register(models.Policy)
admin.site.register(models.DataType)
admin.site.register(models.DataFormat)
admin.site.register(models.ProviderType)
