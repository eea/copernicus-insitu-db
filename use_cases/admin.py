from django.contrib import admin
from use_cases import models

from django.conf import settings


class CopernicusServiceAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]


class UseCaseAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class ThemeAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ["source"]


if settings.USE_CASES_FEATURE_TOGGLE:
    admin.site.register(models.CopernicusService, CopernicusServiceAdmin)
    admin.site.register(models.Country, CountryAdmin)
    admin.site.register(models.UseCase, UseCaseAdmin)
    admin.site.register(models.Theme, ThemeAdmin)
    admin.site.register(models.Reference, ReferenceAdmin)
