# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from insitu import models


class CopernicusServiceAdmin(admin.ModelAdmin):
    search_fields = ['name', 'acronym']
    list_display = ('acronym', 'name', 'website')


class EntrustedEntityAdmin(admin.ModelAdmin):
    search_fields = ['acronym', 'name']
    list_display = ('acronym', 'name', 'website')


class ComponentAdmin(admin.ModelAdmin):
    search_fields = ['acronym', 'name']
    list_display = ('acronym', 'name', 'service', 'entrusted_entity')
    list_filter = ('service', 'entrusted_entity')


class BaseDisplayDeleteAdminMixin:
    list_display = ('__str__', '_deleted',)
    list_filter = ('_deleted',)
    filter_model = None

    def get_queryset(self, request):
        return self.filter_model.objects.really_all()


class ProductRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.ProductRequirement


class DataRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.DataRequirement


class DataProviderRelationAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.DataProviderRelation

admin.site.register(models.CopernicusService, CopernicusServiceAdmin)
admin.site.register(models.EntrustedEntity, EntrustedEntityAdmin)
admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.Requirement)
admin.site.register(models.Product)
admin.site.register(models.ProductRequirement, ProductRequirementAdmin)
admin.site.register(models.DataProvider)
admin.site.register(models.DataProviderDetails)
admin.site.register(models.Data)
admin.site.register(models.DataRequirement, DataRequirementAdmin)
admin.site.register(models.DataProviderRelation, DataProviderRelationAdmin)
admin.site.register(models.Metric)
