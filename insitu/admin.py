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


class CopernicusResponsibleAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'service__name']
    list_display = ('user', 'service')


class DataProviderAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'responsible__name']
    list_display = ('user', 'responsible')


class CountryResponsible(admin.ModelAdmin):
    search_fields = ['user__username', 'country__name']
    list_display = ('user', 'country')


admin.site.register(models.CopernicusService, CopernicusServiceAdmin)
admin.site.register(models.EntrustedEntity, EntrustedEntityAdmin)
admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.Requirement)
admin.site.register(models.Product)
admin.site.register(models.ProductRequirement)
admin.site.register(models.DataResponsible)
admin.site.register(models.DataResponsibleDetails)
admin.site.register(models.Data)
admin.site.register(models.DataRequirement)
admin.site.register(models.DataResponsibleRelation)
admin.site.register(models.Metric)

admin.site.register(models.CopernicusResponsible, CopernicusResponsibleAdmin)
admin.site.register(models.DataProvider, DataProviderAdmin)
admin.site.register(models.CountryResponsible, CountryResponsible)
