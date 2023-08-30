from django.contrib import admin
from use_cases import models


@admin.register(models.CopernicusService)
class CopernicusServiceAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]


@admin.register(models.UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    search_fields = ["title"]


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(models.Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ["source"]
