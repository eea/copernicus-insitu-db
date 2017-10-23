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


class CopernicusProviderAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'service__name']
    list_display = ('user', 'service')


class DataProviderUserAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'provider__name']
    list_display = ('user', 'provider')


class CountryProvider(admin.ModelAdmin):
    search_fields = ['user__username', 'country__name']
    list_display = ('user', 'country')


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

admin.site.register(models.CopernicusProvider, CopernicusProviderAdmin)
admin.site.register(models.DataProviderUser, DataProviderUserAdmin)
admin.site.register(models.CountryProvider, CountryProvider)
