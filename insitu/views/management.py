from django.apps import apps
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.generic import TemplateView
from django.utils import timezone

from insitu.forms import StatisticsDataForm
from insitu.views.protected import (
    IsPublicUser,
    IsSuperuser,
)
from insitu.views.protected.views import ProtectedTemplateView

from insitu.utils import PICKLISTS_DESCRIPTION
from picklists import models
from insitu.models import Product, Requirement, Data, DataProvider, ChangeLog, Release
from insitu.models import Component, CopernicusService, EntrustedEntity


class TransferOwnership(ProtectedTemplateView):
    permission_classes = (IsSuperuser,)

    def post(self, request):
        old_user = request.POST["old_user"]
        new_user = request.POST["new_user"]
        disable_old_user = request.POST["disable_old_user"]
        if old_user == new_user:
            messages.error(
                self.request, "You cannot transfer ownership to the same user!"
            )
        else:

            def transfer_ownership_on_objects(obj):
                new_u = User.objects.get(id=new_user)
                for data_object in obj:
                    data_object.created_by = new_u
                    data_object.save()
                    obj = data_object.get_related_objects()
                    for related_object in obj:
                        related_object.created_by = new_u
                        related_object.save()

            objects = Requirement.objects.filter(created_by=old_user)
            transfer_ownership_on_objects(objects)
            objects = Data.objects.filter(created_by=old_user)
            transfer_ownership_on_objects(objects)
            objects = DataProvider.objects.filter(created_by=old_user)
            transfer_ownership_on_objects(objects)

            if disable_old_user == "yes":
                old_u = User.objects.get(id=old_user)
                old_u.is_active = False
                old_u.save()
                messages.success(self.request, "Previous owner successfully disabled")
            messages.success(self.request, "Ownership successfully transferred")

        return redirect("manage")


class Manager(ProtectedTemplateView):
    template_name = "manage.html"
    permission_classes = (IsSuperuser,)
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StatisticsDataForm()
        context["users"] = User.objects.all()
        return context

    def get_statistics(self, model, **kwargs):
        context = {}
        context["selected_object"] = dict(self.form.fields["selected_object"].choices)[
            kwargs["selected_object"]
        ]
        context["no_of_objects"] = (
            model.objects.really_all()
            .filter(
                Q(created_at__date__lte=kwargs["end_date"], _deleted=False)
                | Q(
                    created_at__date__lte=kwargs["end_date"],
                    updated_at__date__gte=kwargs["end_date"],
                    _deleted=True,
                )
            )
            .count()
        )
        context["no_of_objects_created"] = model.objects.filter(
            created_at__date__lte=kwargs["end_date"],
            created_at__date__gte=kwargs["start_date"],
        ).count()
        context["no_of_objects_updated"] = model.objects.filter(
            updated_at__date__lte=kwargs["end_date"],
            updated_at__date__gte=kwargs["start_date"],
        ).count()
        return context

    def post(self, request, *args, **kwargs):
        self.form = StatisticsDataForm(request.POST, initial=request.POST)
        if self.form.is_valid():
            model = apps.get_model(
                app_label="insitu",
                model_name=self.form.cleaned_data["selected_object"],
            )
            data = self.get_statistics(model, **self.form.cleaned_data)
            data["form"] = StatisticsDataForm(initial=request.POST)
            return render(request, "manage.html", context=data)
        else:
            return render(request, "manage.html", context={"form": self.form})


class HelpPage(ProtectedTemplateView):
    template_name = "help.html"
    permission_classes = (IsPublicUser,)
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["models"] = dict()

        PICKLISTS = [
            models.Area,
            models.Barrier,
            models.ComplianceLevel,
            Component,
            CopernicusService,
            models.Criticality,
            models.Country,
            models.DataFormat,
            models.DataPolicy,
            "data_provider_definitions",
            "data_provider_roles",
            models.DataType,
            models.DefinitionLevel,
            models.Dissemination,
            EntrustedEntity,
            models.EssentialVariable,
            models.InspireTheme,
            "metrics",
            models.ProductGroup,
            models.ProviderType,
            models.Relevance,
            models.RequirementGroup,
            models.QualityControlProcedure,
            "state",
            models.Status,
            models.Timeliness,
            models.UpdateFrequency,
        ]

        for model in PICKLISTS:
            if type(model) is str:
                data = {
                    "non_standard": True,
                    "nice_name": model.replace("_", " ").capitalize(),
                }
                context["models"][model] = data
            else:
                sorting_field = "pk"
                if "sort_order" in [field.name for field in model._meta.fields]:
                    sorting_field = "sort_order"
                data = {
                    "nice_name": model._meta.verbose_name,
                    "description": PICKLISTS_DESCRIPTION.get(model.__name__, None),
                    "objects": model.objects.order_by(sorting_field),
                    "fields": [
                        field.name
                        for field in model._meta.fields
                        if field.name not in ("id", "sort_order")
                    ],
                    "non_standard": False,
                }
                context["models"][model._meta.model_name] = data
        context["email"] = settings.SUPPORT_EMAIL
        return context


class AboutView(TemplateView):
    template_name = "about.html"

    def statistics(self):
        return {
            "products": Product.objects.all().count(),
            "requirements": Requirement.objects.all().count(),
            "data": Data.objects.all().count(),
            "data_providers": DataProvider.objects.all().count(),
            "logged_users": Session.objects.filter(
                expire_date__gte=timezone.now()
            ).count(),
            "change_logs": ChangeLog.objects.all().order_by("-created_at"),
            "releases": Release.objects.all().order_by("-current", "-created_at"),
            "registered_users": User.objects.all().count(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(**self.statistics())
        return context
