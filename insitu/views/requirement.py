from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy

from django_fsm import has_transition_perm

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices, WORKFLOW_STATES
from insitu.views.base import (
    ESDatatableView,
    CreatedByMixin,
    ChangesRequestedMailMixin,
)
from insitu.views.protected import (
    ProtectedTemplateView,
    ProtectedDetailView,
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView,
    LoggingTransitionProtectedDetailView,
)
from insitu.views.protected.permissions import (
    IsAuthenticated,
    IsDraftObject,
    IsOwnerUser,
    IsNotReadOnlyUser,
)
from picklists import models as pickmodels


class GetInitialMixin:
    def get_requirement(self):
        try:
            return self.get_object()
        except AttributeError:
            pk = self.request.GET.get("pk", None)
            try:
                return models.Requirement.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return

    def get_initial(self):
        requirement = self.get_requirement()
        if not requirement:
            return super().get_initial()

        initial_data = super().get_initial()
        for field in [
            "name",
            "note",
            "dissemination",
            "owner",
            "quality_control_procedure",
            "group",
        ]:
            initial_data[field] = getattr(requirement, field)
        for field in [
            "uncertainty",
            "update_frequency",
            "timeliness",
            "scale",
            "horizontal_resolution",
            "vertical_resolution",
        ]:
            for attr in ["threshold", "breakthrough", "goal"]:
                initial_data["__".join([field, attr])] = getattr(
                    getattr(requirement, field), attr
                )
        return initial_data.copy()


class RequirementDetail(ProtectedDetailView):
    template_name = "requirement/detail.html"
    model = models.Requirement
    context_object_name = "requirement"
    permission_classes = ()
    target_type = "requirement"

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse("auth:login")
        return super().permission_denied(request)

    def get_object(self):
        if hasattr(self, "object"):
            return self.object
        else:
            self.object = (
                self.model.objects.select_related(
                    "dissemination",
                    "quality_control_procedure",
                    "group",
                    "uncertainty",
                    "update_frequency",
                    "timeliness",
                    "horizontal_resolution",
                    "scale",
                    "vertical_resolution",
                    "status",
                    "created_by",
                )
                .prefetch_related(
                    "product_requirements",
                    "product_requirements__product",
                    "product_requirements__level_of_definition",
                    "product_requirements__relevance",
                    "product_requirements__criticality",
                    "product_requirements__barriers",
                    "product_requirements__created_by",
                    "datarequirement_set",
                    "datarequirement_set__data",
                    "datarequirement_set__level_of_compliance",
                    "datarequirement_set__created_by",
                    "datarequirement_set__created_by__team__teammates",
                    "product_requirements__created_by__team__teammates",
                    "created_by__team__teammates",
                )
                .get(pk=self.kwargs["pk"])
            )
            return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_groups"] = self.request.user.groups.values_list(
            "name", flat=True
        )
        return context


class RequirementList(ProtectedTemplateView):
    template_name = "requirement/list.html"
    permission_classes = ()
    target_type = "requirements"

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse("auth:login")
        return super().permission_denied(request)

    def get_context_data(self):
        context = super(RequirementList, self).get_context_data()
        disseminations = get_choices("name", model_cls=pickmodels.Dissemination)
        products = get_choices("name", model_cls=models.Product)
        quality_control_procedures = get_choices(
            "name", model_cls=pickmodels.QualityControlProcedure
        )
        groups = get_choices("name", model_cls=pickmodels.RequirementGroup)
        states = [{"title": "All", "name": "All"}] + [
            {"title": title, "name": name} for name, title in WORKFLOW_STATES
        ]
        components = get_choices("name", model_cls=models.Component)
        context.update(
            {
                "disseminations": disseminations,
                "products": products,
                "quality_control_procedures": quality_control_procedures,
                "groups": groups,
                "states": states,
                "components": components,
            }
        )
        return context


class RequirementListJson(ESDatatableView):
    columns = [
        "id",
        "name",
        "dissemination",
        "quality_control_procedure",
        "group",
        "uncertainty",
        "update_frequency",
        "timeliness",
        "scale",
        "horizontal_resolution",
        "vertical_resolution",
        "state",
    ]
    order_columns = columns
    filter_translation = {
        "product": "products.product",
        "component": "components.component",
    }
    #  Translates a querystring parameter to an ES Document field with a
    #  different name.
    filters = [
        "dissemination",
        "quality_control_procedure",
        "group",
        "product",
        "state",
        "component",
    ]  # These are the querystring parameters we expect.
    filter_fields = [
        "dissemination__name",
        "quality_control_procedure__name",
        "group__name",
        "products__name",
        "state",
        "products__component__name",
    ]  # These are the corresponding model fields, in the same order.
    document = documents.RequirementDoc
    permission_classes = ()


class RequirementAdd(GetInitialMixin, CreatedByMixin, LoggingProtectedCreateView):
    template_name = "requirement/add.html"
    model = models.Requirement
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    target_type = "requirement"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The requirement was created successfully!")
        return response

    def get_form_class(self):
        requirement = self.get_requirement()
        if requirement:
            self.post_action = "cloned requirement {pk} to".format(pk=requirement.pk)
            self.post_action_failed = "tried to clone object {pk} of".format(
                pk=requirement.pk
            )
            return forms.RequirementCloneForm
        return forms.RequirementForm

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse("requirement:list")
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.object
        return reverse("requirement:detail", kwargs={"pk": instance.pk})


class RequirementEdit(GetInitialMixin, LoggingProtectedUpdateView):
    template_name = "requirement/edit.html"
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = "requirement"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    target_type = "requirement"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The requirement was updated successfully!")
        return response

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse("requirement:list")
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.get_object()
        return reverse("requirement:detail", kwargs={"pk": instance.pk})


class RequirementDelete(LoggingProtectedDeleteView):
    template_name = "requirement/delete.html"
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = "requirement"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    target_type = "requirement"

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse("requirement:list")
        return super().permission_denied(request)

    def get_success_url(self):
        messages.success(self.request, "The requirement was deleted successfully!")
        return reverse("requirement:list")


class RequirementTransition(
    ChangesRequestedMailMixin, LoggingTransitionProtectedDetailView
):
    model = models.Requirement
    template_name = "requirement/transition.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    context_object_name = "requirement"
    target_type = "requirement"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition_name = self.kwargs.get("transition")

        transition = getattr(self.object, transition_name, None)
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
        requirement = self.get_object(self.get_queryset())
        return reverse("requirement:detail", kwargs={"pk": requirement.pk})

    def post(self, request, *args, **kwargs):
        requirement = self.get_object(self.get_queryset())
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition_name = self.kwargs.get("transition")

        transition = getattr(requirement, transition_name, None)
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
        requirement.requesting_user = self.request.user
        transition()
        requirement.save()
        feedback = ""
        if transition_name == "request_changes":
            requirement.feedback = ""
            requirement.feedback = request.POST.get("feedback", "")
            requirement.save()
            feedback = request.POST.get("feedback", "")
            self.send_mail(requirement, requirement.name, feedback)
        return HttpResponseRedirect(
            reverse("requirement:detail", kwargs={"pk": requirement.pk})
        )
        raise Http404()


class RequirementClearFeedback(LoggingProtectedCreateView):
    model = models.Requirement
    context_object_name = "requirement"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("requirement:list")
    target_type = "requirement"

    def post(self, request, *args, **kwargs):
        requirement = self.get_object(self.get_queryset())
        requirement.feedback = ""
        requirement.save()
        return HttpResponseRedirect(
            reverse("requirement:detail", kwargs={"pk": requirement.pk})
        )
