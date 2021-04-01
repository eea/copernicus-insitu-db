# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from xworkflows import ForbiddenTransition

from insitu import documents
from insitu import models
from insitu import forms
from insitu.views.base import (
    ESDatatableView,
    CreatedByMixin,
    ChangesRequestedMailMixin,
)
from insitu.views.protected import ProtectedUpdateView
from insitu.views.protected import (
    ProtectedTemplateView,
    ProtectedDetailView,
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView,
    LoggingTransitionProtectedDetailView,
)
from insitu.views.protected import IsAuthenticated, IsNotReadOnlyUser
from insitu.views.protected.permissions import IsOwnerUser, IsDraftObject
from insitu.utils import get_choices

from picklists import models as pickmodels


class DataProviderList(ProtectedTemplateView):
    template_name = "data_provider/list.html"
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy("auth:login")
    target_type = "data providers"

    def get_context_data(self):
        context = super().get_context_data()
        provider_types = get_choices("name", model_cls=pickmodels.ProviderType)
        states = [{"title": "All", "name": "All"}] + [
            state for state in models.ValidationWorkflow.states
        ]
        components = get_choices("name", model_cls=models.Component)
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
    permission_classes = (IsAuthenticated,)


class DataProviderDetail(ProtectedDetailView):
    model = models.DataProvider
    context_object_name = "provider"
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_template_names(self):
        provider = self.object
        if provider.is_network:
            return ["data_provider/network/detail.html"]
        return ["data_provider/non_network/detail.html"]


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
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
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
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
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
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
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
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
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
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "data provider"

    def get_success_url(self):
        messages.success(self.request, "The data provider was deleted successfully!")
        return reverse("provider:list")


class DataProviderTransition(
    ChangesRequestedMailMixin, LoggingTransitionProtectedDetailView
):
    model = models.DataProvider
    template_name = "data_provider/transition.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    context_object_name = "provider"
    target_type = "data provider"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition = models.ValidationWorkflow.get_transition(source, target)
        if not transition:
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
        self.post_action = "changed state from {source} to {target} for".format(
            source=source, target=target
        )
        id = self.get_object_id()
        self.log_action(request, self.post_action, id)
        try:
            transition_name = models.ValidationWorkflow.get_transition(source, target)
            transition = getattr(data_provider, transition_name)
            data_provider.requesting_user = self.request.user
            if transition.is_available():
                transition()
                feedback = ""
                if transition_name == "request_changes":
                    data_provider.feedback = ""
                    data_provider.feedback = request.POST.get("feedback", "")
                    data_provider.save()
                    feedback = request.POST.get("feedback", "")
                if self.transition_name == transition_name:
                    self.send_mail(data_provider, feedback)
                return HttpResponseRedirect(
                    reverse("provider:detail", kwargs={"pk": data_provider.pk})
                )
        except ForbiddenTransition:
            pass
        raise Http404()

class DataProviderClearFeedback(LoggingProtectedCreateView):
    model = models.DataProvider
    context_object_name = "provider"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("provider:list")
    target_type = "provider"

    def post(self, request, *args, **kwargs):
        provider = self.get_object(self.get_queryset())
        provider.feedback = ""
        provider.save()
        return HttpResponseRedirect(
            reverse("provider:detail", kwargs={"pk": provider.pk})
        )
