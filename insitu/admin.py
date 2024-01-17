# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.crypto import get_random_string

from guardian.admin import GuardedModelAdmin

from insitu import models
from insitu.utils import export_logs_excel
from insitu.forms import CreateUserForm, UserEditAdminForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.admin import UserAdmin
from markdownx.admin import MarkdownxModelAdmin


class TeamInline(admin.TabularInline):
    model = models.Team
    fields = ("teammates",)


class InsituUserAdmin(UserAdmin):
    form = UserEditAdminForm
    inlines = [TeamInline]
    add_form = CreateUserForm
    add_fieldsets = [
        (
            None,
            {
                "fields": ["email", "username"],
            },
        ),
        (
            "Personal info",
            {
                "fields": ["first_name", "last_name"],
            },
        ),
    ]
    fieldsets = [
        (
            None,
            {
                "fields": ["email"],
            },
        ),
        (
            "Personal info",
            {
                "fields": ["username", "first_name", "last_name"],
            },
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                ],
            },
        ),
        (
            "Important dates",
            {
                "fields": ["date_joined", "last_login"],
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        is_new_user = obj.pk is None

        if is_new_user:
            obj.set_password(get_random_string())

        super().save_model(request, obj, form, change)

        if is_new_user:
            reset_form = PasswordResetForm({"email": obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                subject_template_name="mails/password_set_subject.txt",
                html_email_template_name="mails/password_set_email.html",
            )

    def get_inline_instances(self, request, obj=None):
        return obj and super(UserAdmin, self).get_inline_instances(request, obj) or []


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


if settings.DELIVERIES_FEATURE_TOGGLE:

    @admin.register(models.Delivery)
    class DeliveryAdmin(MarkdownxModelAdmin):
        search_fields = ["version", "current"]
        list_display = ("version", "description", "created_at", "current")


@admin.register(models.LoggedAction)
class LoggedActionAdmin(GuardedModelAdmin):
    readonly_fields = ("logged_date",)
    search_fields = ["logged_date", "user", "target_type", "id_target"]
    list_display = (
        "logged_date",
        "user",
        "action",
        "target_type",
        "id_target",
        "extra",
    )
    actions = [logs_export_as_excel]

    logs_export_as_excel.short_description = "Export logs as Excel"


@admin.register(models.Component)
class ComponentAdmin(admin.ModelAdmin):
    search_fields = ["acronym", "name"]
    list_display = ("acronym", "name", "service", "entrusted_entity")
    list_filter = ("service", "entrusted_entity")


@admin.register(models.Requirement)
class RequirementAdmin(GuardedModelAdmin):
    readonly_fields = (
        "components",
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    list_display = ("id", "name", "state")
    list_filter = ("state",)

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
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    list_display = ("id", "name", "state")
    list_filter = ("state",)


@admin.register(models.DataProvider)
class DataProviderAdmin(GuardedModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    list_display = ("id", "name", "get_countries", "state")
    list_filter = ("state", "countries")

    def get_countries(self, obj):
        return ",\n".join([c.name for c in obj.countries.all()])

    def get_queryset(self, request):
        queryset = super(DataProviderAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related("countries")
        return queryset


class BaseDisplayDeleteAdminMixin:
    list_display = (
        "__str__",
        "_deleted",
    )
    list_filter = ("_deleted",)
    filter_model = None

    def get_queryset(self, request):
        return self.filter_model.objects.really_all()


@admin.register(models.Metric)
class MetricAdmin(GuardedModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(models.Product)
class ProductAdmin(GuardedModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    search_fields = ["name"]
    list_display = ("id", "name")


@admin.register(models.ProductRequirement)
class ProductRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    filter_model = models.ProductRequirement
    list_display = (
        "__str__",
        "product_id",
        "requirement_id",
        "product__name",
        "requirement__name",
        "state",
    )
    list_filter = ("state", "product_id", "requirement_id")

    @admin.display(ordering="product__name", description="Product")
    def product__name(self, obj):
        return obj.product.name

    @admin.display(ordering="requirement__name", description="Requirement")
    def requirement__name(self, obj):
        return obj.requirement.name

    def get_queryset(self, request):
        queryset = super(ProductRequirementAdmin, self).get_queryset(request)
        queryset = queryset.select_related("requirement", "product")
        return queryset


@admin.register(models.DataRequirement)
class DataRequirementAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    filter_model = models.DataRequirement
    list_display = (
        "__str__",
        "requirement_id",
        "data_id",
        "data__name",
        "requirement__name",
        "state",
    )
    list_filter = ("state", "data_id", "requirement_id")

    @admin.display(ordering="data__name", description="Data")
    def data__name(self, obj):
        return obj.data.name

    @admin.display(ordering="requirement__name", description="Requirement")
    def requirement__name(self, obj):
        return obj.requirement.name

    def get_queryset(self, request):
        queryset = super(DataRequirementAdmin, self).get_queryset(request)
        queryset = queryset.select_related("requirement", "data")
        return queryset


@admin.register(models.DataProviderRelation)
class DataProviderRelationAdmin(BaseDisplayDeleteAdminMixin, admin.ModelAdmin):
    filter_model = models.DataProviderRelation
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = (
        "__str__",
        "data_id",
        "provider_id",
        "provider__name",
        "data__name",
        "role",
    )
    list_filter = ("data_id", "provider_id")

    @admin.display(ordering="provider__name", description="Data Provider")
    def provider__name(self, obj):
        return obj.provider.name

    @admin.display(ordering="data__name", description="Data")
    def data__name(self, obj):
        return obj.data.name

    def get_queryset(self, request):
        queryset = super(DataProviderRelationAdmin, self).get_queryset(request)
        queryset = queryset.select_related("data", "provider")
        return queryset


@admin.register(models.DataProviderDetails)
class DataProviderDetailsAdmin(GuardedModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = (
        "__str__",
        "data_provider_id",
        "data_provider__name",
        "provider_type",
    )
    list_filter = ("data_provider_id",)

    @admin.display(ordering="data_provider__name", description="Data Provider")
    def data_provider__name(self, obj):
        return obj.data_provider.name


@admin.register(models.Team)
class Team(admin.ModelAdmin):
    list_display = ("user",)


admin.site.unregister(User)
admin.site.register(User, InsituUserAdmin)
