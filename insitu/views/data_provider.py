# -*- coding: utf-8 -*-
from django.contrib import messages
from copernicus.settings import SITE_URL
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse, reverse_lazy
from django_fsm import has_transition_perm
from django.db.models import Subquery, OuterRef
from insitu import documents
from insitu.models import Component, DataProvider, DataProviderDetails
from insitu import forms
from insitu.views.base import (
    ESDatatableView,
    CreatedByMixin,
    ChangesRequestedMailMixin,
)
from insitu.views.protected import ProtectedUpdateView
from insitu.views.protected import (
    ProtectedView,
    ProtectedTemplateView,
    ProtectedDetailView,
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView,
    LoggingTransitionProtectedDetailView,
)
from insitu.views.protected import IsAuthenticated, IsNotReadOnlyUser, HasToken
from insitu.views.protected.permissions import (
    IsDataProviderAndDataEditorUser,
    IsPublicUser,
    IsDraftObject,
)
from insitu.utils import get_choices, WORKFLOW_STATES

from picklists import models as pickmodels


class DataProviderList(ProtectedTemplateView):
    template_name = "data_provider/list.html"
    permission_classes = (IsPublicUser,)
    permission_denied_redirect = reverse_lazy("auth:login")
    target_type = "data providers"

    def get_context_data(self):
        context = super().get_context_data()
        provider_types = get_choices("name", model_cls=pickmodels.ProviderType)
        states = [{"title": "All", "name": "All"}] + [
            {"title": title, "name": name} for name, title in WORKFLOW_STATES
        ]
        components = get_choices("name", model_cls=Component)
        context.update(
            {
                "provider_types": provider_types,
                "states": states,
                "components": components,
            }
        )
        return context


class DataProviderListJson(ESDatatableView):
    columns = [
        "name",
        "acronym",
        "edmo",
        "address",
        "phone",
        "email",
        "contact_person",
        "provider_type",
        "is_network",
        "state",
    ]
    order_columns = columns
    filter_translation = {
        "component": "components.name",
    }
    filters = ["is_network", "provider_type", "state", "component"]
    filter_fields = [
        "is_network",
        "details__provider_type__name",
        "state",
        "data__requirements__products__component__name",
    ]
    document = documents.DataProviderDoc
    permission_classes = (IsPublicUser,)


class DataProviderDetail(ProtectedDetailView):
    model = DataProvider
    context_object_name = "provider"
    permission_classes = (IsPublicUser,)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_object(self):
        if hasattr(self, "object"):
            return self.object
        else:
            try:
                self.object = (
                    self.model.objects.select_related("created_by")
                    .prefetch_related(
                        "details",
                        "details__provider_type",
                        "created_by__team",
                        "dataproviderrelation_set",
                        "dataproviderrelation_set__data",
                    )
                    .get(pk=self.kwargs["pk"])
                )
            except self.model.DoesNotExist:
                raise Http404()
            return self.object

    def get_template_names(self):
        provider = self.object
        if provider.is_network:
            return ["data_provider/network/detail.html"]
        return ["data_provider/non_network/detail.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_groups"] = self.request.user.groups.values_list(
            "name", flat=True
        )
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response


class DataProviderAddNetwork(CreatedByMixin, LoggingProtectedCreateView):
    template_name = "data_provider/network/add.html"
    form_class = forms.DataProviderNetworkForm
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider network"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "details" not in context:
            context["details"] = forms.DataProviderDetailsForm()
        return context

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        super().form_valid(form)
        data = form.data.copy()
        data["data_provider"] = self.object.pk
        details_form = forms.DataProviderDetailsForm(data=data)
        details_form.save(created_by=self.object.created_by)
        messages.success(
            self.request, "The data provider network was created successfully!"
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(
            self.get_context_data(form=form, details=details_form)
        )

    def get_success_url(self):
        return reverse("provider:detail", kwargs={"pk": self.object.pk})


class DataProviderAddNonNetwork(CreatedByMixin, LoggingProtectedCreateView):
    template_name = "data_provider/non_network/add.html"
    form_class = forms.DataProviderNonNetworkForm
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "details" not in context:
            context["details"] = forms.DataProviderDetailsForm()
        return context

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        super().form_valid(form)
        data = form.data.copy()
        data["data_provider"] = self.object.pk
        details_form = forms.DataProviderDetailsForm(data=data)
        details_form.save(created_by=self.object.created_by)
        messages.success(self.request, "The data provider was created successfully!")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(
            self.get_context_data(form=form, details=details_form)
        )

    def get_success_url(self):
        return reverse("provider:detail", kwargs={"pk": self.object.pk})


class DataProviderEditNetwork(LoggingProtectedUpdateView):
    template_name = "data_provider/network/edit.html"
    form_class = forms.DataProviderNetworkForm
    context_object_name = "provider"
    model = DataProvider
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider network"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "details" not in context:
            details = self.object.details.first()
            context["details"] = forms.DataProviderDetailsForm(instance=details)
        return context

    def _update_objects(self, form):
        self.object = form.save()
        details = self.object.details.first()
        data = form.data.copy()
        data["data_provider"] = self.object.pk
        details_form = forms.DataProviderDetailsForm(instance=details, data=data)
        details_form.save()

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        self._update_objects(form)
        messages.success(
            self.request, "The data provider network was updated successfully!"
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(
            self.get_context_data(form=form, details=details_form)
        )

    def get_success_url(self):
        return reverse("provider:detail", kwargs={"pk": self.object.pk})


class DataProviderEditNonNetwork(LoggingProtectedUpdateView):
    template_name = "data_provider/non_network/edit.html"
    form_class = forms.DataProviderNonNetworkForm
    context_object_name = "provider"
    model = DataProvider
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "details" not in context:
            details = self.object.details.first()
            context["details"] = forms.DataProviderDetailsForm(instance=details)
        return context

    def _update_objects(self, form):
        self.object = form.save()
        details = self.object.details.first()
        data = form.data.copy()
        data["data_provider"] = self.object.pk
        details_form = forms.DataProviderDetailsForm(instance=details, data=data)
        details_form.save()

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        self._update_objects(form)
        messages.success(self.request, "The data provider was updated successfully!")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(
            self.get_context_data(form=form, details=details_form)
        )

    def get_success_url(self):
        return reverse("provider:detail", kwargs={"pk": self.object.pk})


class DataProviderEditNetworkMembers(ProtectedUpdateView):
    template_name = "data_provider/network/edit_members.html"
    form_class = forms.DataProviderNetworkMembersForm
    context_object_name = "provider"
    model = DataProvider
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "The members for this data provider network were updated successfully!",
        )
        return response

    def get_success_url(self):
        return reverse("provider:detail", kwargs={"pk": self.object.pk})


class DataProviderDeleteNetwork(LoggingProtectedDeleteView):
    template_name = "data_provider/network/delete.html"
    form_class = forms.DataProviderNetworkForm
    context_object_name = "provider"
    model = DataProvider
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider network"

    def get_success_url(self):
        messages.success(
            self.request, "The data provider network was deleted successfully!"
        )
        return reverse("provider:list")


class DataProviderDeleteNonNetwork(LoggingProtectedDeleteView):
    template_name = "data_provider/non_network/delete.html"
    form_class = forms.DataProviderNonNetworkForm
    context_object_name = "provider"
    model = DataProvider
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_success_url(self):
        messages.success(self.request, "The data provider was deleted successfully!")
        return reverse("provider:list")


class DataProviderTransition(
    ChangesRequestedMailMixin, LoggingTransitionProtectedDetailView
):
    model = DataProvider
    template_name = "data_provider/transition.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    context_object_name = "provider"
    target_type = "data provider"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition = self.kwargs.get("transition")
        transition = getattr(self.object, transition, None)
        try:
            if not has_transition_perm(transition, self.request.user):
                raise Http404()
        except AttributeError:
            raise Http404()
        objects = [
            {"obj": item, "type": item.__class__.__name__}
            for item in self.object.get_related_objects()
        ]
        context.update(
            {
                "target": target,
                "source": source,
                "objects": objects,
            }
        )
        return context

    def get_success_url(self, **kwargs):
        data_provider = self.get_object(self.get_queryset())
        return reverse("provider:detail", kwargs={"pk": data_provider.pk})

    def post(self, request, *args, **kwargs):
        data_provider = self.get_object(self.get_queryset())
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition_name = self.kwargs.get("transition")
        transition = getattr(data_provider, transition_name, None)
        try:
            if not has_transition_perm(transition, self.request.user):
                raise Http404()
        except AttributeError:
            raise Http404()
        self.post_action = "changed state from {source} to {target} for".format(
            source=source, target=target
        )
        id = self.get_object_id()
        self.log_action(request, self.post_action, id)
        data_provider.requesting_user = self.request.user
        transition()
        data_provider.save()
        feedback = ""
        if transition_name == "request_changes":
            data_provider.feedback = ""
            data_provider.feedback = request.POST.get("feedback", "")
            data_provider.save()
            feedback = request.POST.get("feedback", "")
            self.send_mail(data_provider, data_provider.name, feedback)
        return HttpResponseRedirect(
            reverse("provider:detail", kwargs={"pk": data_provider.pk})
        )
        raise Http404()


class DataProviderClearFeedback(LoggingProtectedCreateView):
    model = DataProvider
    context_object_name = "provider"
    permission_classes = (
        IsDataProviderAndDataEditorUser,
        IsDraftObject,
        IsNotReadOnlyUser,
    )
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "provider"

    def post(self, request, *args, **kwargs):
        provider = self.get_object(self.get_queryset())
        provider.feedback = ""
        provider.save()
        return HttpResponseRedirect(
            reverse("provider:detail", kwargs={"pk": provider.pk})
        )


class DataProviderListApiView(ProtectedView):
    permission_classes = (HasToken,)

    def get(self, request, *args, **kwargs):
        data = []
        data_providers = (
            DataProvider.objects.all()
            .prefetch_related(
                "countries",
                "members",
                "dataproviderrelation_set__data",
                "dataproviderrelation_set",
                "dataproviderrelation_set__data__requirements",
                "dataproviderrelation_set__data__requirements__group",
            )
            .annotate(
                acronym=Subquery(
                    DataProviderDetails.objects.filter(
                        data_provider=OuterRef("pk"), _deleted=False
                    ).values_list("acronym", flat=True)[:1]
                ),
                website=Subquery(
                    DataProviderDetails.objects.filter(
                        data_provider=OuterRef("pk"), _deleted=False
                    ).values_list("website", flat=True)[:1]
                ),
                provider_type=Subquery(
                    DataProviderDetails.objects.filter(
                        data_provider=OuterRef("pk")
                    ).values_list("provider_type__name", flat=True)[:1]
                ),
            )
        )

        for provider in data_providers:
            requirement_groups = []
            for dp_relation in provider.dataproviderrelation_set.all():
                data_requirement_groups = [
                    x.group for x in dp_relation.data.requirements.all()
                ]
                for group in data_requirement_groups:
                    if group not in requirement_groups:
                        requirement_groups.append(group)
            entry = {
                "id": provider.id,
                "acronym": provider.acronym,
                "name": provider.name,
                "native_name": provider.native_name,
                "provider_type": provider.provider_type,
                "countries": [
                    {"code": country.code, "name": country.name}
                    for country in provider.countries.all()
                ],
                "link": SITE_URL
                + reverse("provider:detail", kwargs={"pk": provider.id}),
                "members": [member.id for member in provider.members.all()],
                "website": provider.website,
                "requirement_groups": [
                    {"id": requirement_group.id, "name": requirement_group.name}
                    for requirement_group in requirement_groups
                ],
                "is_network": provider.is_network,
            }
            data.append(entry)
        return JsonResponse(data, safe=False)
