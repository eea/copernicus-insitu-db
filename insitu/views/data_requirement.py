from django.contrib import messages
from django.urls import reverse_lazy

from insitu import models
from insitu import forms
from insitu.views.base import CreatedByMixin
from insitu.views.protected import (
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView,
)
from insitu.views.protected.permissions import (
    IsAuthenticated,
    IsDraftObject,
    IsOwnerUser,
    IsNotReadOnlyUser,
)


class DataRequirementAdd(CreatedByMixin, LoggingProtectedCreateView):
    template_name = "data/requirement/add.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("requirement:list")
    form_class = forms.RequirementDataRequirementForm
    form_field = "requirement"
    model = models.Requirement
    title = "Add a new data for {}"
    target_type = "relation between data and requirement"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "The relation between data and requirement was created successfully!",
        )
        return response

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.kwargs["requirement_pk"]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(
            pk=self.kwargs["requirement_pk"]
        )
        context["title"] = self.title.format(context[self.form_field].name)
        context["url"] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "requirement:detail", kwargs={"pk": self.kwargs["requirement_pk"]}
        )


class DataRequirementEdit(LoggingProtectedUpdateView):
    model = models.DataRequirement
    template_name = "data/requirement/edit.html"
    form_class = forms.DataRequirementEditForm
    context_object_name = "rel"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("requirement:list")
    target_type = "relation between data and requirement"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "The relation between data and requirement was updated successfully!",
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url"] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "requirement:detail", kwargs={"pk": self.kwargs["requirement_pk"]}
        )


class DataRequirementDelete(LoggingProtectedDeleteView):
    model = models.DataRequirement
    template_name = "data/requirement/delete.html"
    context_object_name = "rel"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("requirement:list")
    target_type = "relation between data and requirement"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url"] = self.get_success_url()
        return context

    def get_success_url(self):
        if self.request.method != "GET":
            messages.success(
                self.request,
                "The relation between data and requirement was deleted successfully!",
            )
        return reverse_lazy(
            "requirement:detail", kwargs={"pk": self.kwargs["requirement_pk"]}
        )
