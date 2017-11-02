# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from insitu import models


class CopernicusServiceAdmin(admin.ModelAdmin):
    search_fields = ['name', 'acronym']


class EntrustedEntityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'acronym']


class ComponentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'acronym']
    list_display = ('name', 'service', 'entrusted_entity')


admin.site.register(models.CopernicusService, CopernicusServiceAdmin)
admin.site.register(models.EntrustedEntity, EntrustedEntityAdmin)
admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.Requirement)
admin.site.register(models.Product)
admin.site.register(models.ProductRequirement)
admin.site.register(models.DataProvider)
admin.site.register(models.DataProviderDetails)
admin.site.register(models.Data)
admin.site.register(models.DataRequirement)
admin.site.register(models.DataProviderRelation)
admin.site.register(models.Metric)
