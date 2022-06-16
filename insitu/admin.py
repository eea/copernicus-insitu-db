# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from guardian.admin import GuardedModelAdmin

from insitu import models
from insitu.utils import export_logs_excel


def logs_export_as_excel(LoggedActionAdmin, request, queryset):
    return export_logs_excel(queryset)


@admin.register(models.CopernicusService)
class CopernicusServiceAdmin(admin.ModelAdmin):
    search_fields = ["name", "acronym"]
    list_display = ("acronym", "name", "website")


@admin.register(models.EntrustedEntity)
class EntrustedEntityAdmin(admin.ModelAdmin):
    search_fields = ["acronym", "name"]
    list_display = ("acronym", "name", "website")


@admin.register(models.ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    search_fields = ["version", "current"]
    list_display = ("version", "description", "created_at", "current")


@admin.register(models.LoggedAction)
class LoggedActionAdmin(GuardedModelAdmin):
    readonly_fields = ("logged_date", "obj_link")
    search_fields = ["logged_date", "user", "target_type", "id_target"]
    list_display = ("logged_date", "user", "target_type", "obj_link")
    actions = [logs_export_as_excel]

    def obj_link(self, obj):
        if obj.id_target:
            links = [
                '<a href="{}">{}</a>'.format(
                    reverse(
                        f"admin:insitu_{obj.target_type}_change", args=(obj.id_target,)
                    ),
                    obj.id_target,
                )
            ]
            return mark_safe(", ".join(links))

    obj_link.short_description = "Target ID"
    logs_export_as_excel.short_description = "Export logs as Excel"


@admin.register(models.Component)
class ComponentAdmin(admin.ModelAdmin):
    search_fields = ["acronym", "name"]
    list_display = ("acronym", "name", "service", "entrusted_entity")
    list_filter = ("service", "entrusted_entity")


@admin.register(models.Requirement)
class RequirementAdmin(GuardedModelAdmin):
    readonly_fields = ("components",)
    search_fields = ["name"]
    list_display = ("id", "name")

    def components(self, obj):
        links = [
            '<a href="{}">{}</a>'.format(
                reverse("admin:insitu_component_change", args=(component.pk,)),
                component.name,
            )
            for component in obj.components
        ]
        return mark_safe(", ".join(links))

    components.short_description = "components"


@admin.register(models.Data)
class DataAdmin(GuardedModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name")


@admin.register(models.DataProvider)
class DataProviderAdmin(GuardedModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name")


class BaseDisplayDeleteAdminMixin:
    list_display = (
        "__str__",
        "_deleted",
    )
    list_filter = ("_deleted",)
    filter_model = None

    def get_queryset(self, request):
        return self.filter_model.objects.really_all()


@admin.register(models.ProductRequirement)
class ProductRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.ProductRequirement


@admin.register(models.DataRequirement)
class DataRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.DataRequirement


@admin.register(models.DataProviderRelation)
class DataProviderRelationAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.DataProviderRelation


admin.site.register(models.Product)
admin.site.register(models.DataProviderDetails)
admin.site.register(models.Metric)
