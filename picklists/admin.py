# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from picklists import models


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name')

admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.InspireTheme)
admin.site.register(models.ProductStatus)
admin.site.register(models.ProductGroup)
admin.site.register(models.DefinitionLevel)
admin.site.register(models.TargetDistance)
admin.site.register(models.Relevance)
admin.site.register(models.Criticality)
admin.site.register(models.Barrier)
admin.site.register(models.Dissemination)
admin.site.register(models.Coverage)
admin.site.register(models.Quality)
admin.site.register(models.ComplianceLevel)
admin.site.register(models.Frequency)
admin.site.register(models.Timeliness)
admin.site.register(models.Policy)
admin.site.register(models.DataType)
