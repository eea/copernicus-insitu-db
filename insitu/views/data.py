from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.http.response import HttpResponseRedirect
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
from insitu.views.protected import (
    IsAuthenticated,
    IsNotReadOnlyUser,
    IsOwnerUser,
)
from insitu.views.protected.permissions import IsDraftObject
from picklists import models as pickmodels


class DataList(ProtectedTemplateView):
    template_name = "data/list.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")
    target_type = "data"

    def get_context_data(self):
        context = super(DataList, self).get_context_data()
        update_frequencies = get_choices("name", model_cls=pickmodels.UpdateFrequency)
        areas = get_choices("name", model_cls=pickmodels.Area)
        timelinesses = get_choices("name", model_cls=pickmodels.Timeliness)
        data_policies = get_choices("name", model_cls=pickmodels.DataPolicy)
        data_types = get_choices("name", model_cls=pickmodels.DataType)
        data_formats = get_choices("name", model_cls=pickmodels.DataFormat)
        quality_control_procedures = get_choices(
            "name", model_cls=pickmodels.QualityControlProcedure
        )
        requirements = get_choices("name", model_cls=models.Requirement)
        disseminations = get_choices("name", model_cls=pickmodels.Dissemination)
        states = [{"title": "All", "name": "All"}] + [
            {"title": title, "name": name} for name, title in WORKFLOW_STATES
        ]
        components = get_choices("name", model_cls=models.Component)
        context.update(
            {
                "update_frequencies": update_frequencies,
                "areas": areas,
                "timelinesses": timelinesses,
                "data_policies": data_policies,
                "data_types": data_types,
                "data_formats": data_formats,
                "quality_control_procedures": quality_control_procedures,
                "disseminations": disseminations,
                "requirements": requirements,
                "states": states,
                "components": components,
            }
        )
        return context


class DataListJson(ESDatatableView):
    columns = [
        "name",
        "update_frequency",
        "area",
        "timeliness",
        "data_policy",
        "data_type",
        "data_format",
        "quality_control_procedure",
        "dissemination",
        "state",
    ]
    order_columns = columns
    filter_translation = {
        "requirement": "requirements.requirement",
        "component": "components.name",
    }
    filters = [
        "update_frequency",
        "area",
        "timeliness",
        "data_policy",
        "data_type",
        "data_format",
        "quality_control_procedure",
        "dissemination",
        "requirement",
        "state",
        "component",
    ]
    filter_fields = [
        "update_frequency__name",
        "area__name",
        "timeliness__name",
        "data_policy__name",
        "data_type__name",
        "data_format__name",
        "quality_control_procedure__name",
        "dissemination__name",
        "requirements__name",
        "state",
        "requirements__products__component__name",
    ]

    extra_filters = {
        "requirements___deleted": False,
        "datarequirement___deleted": False,
    }

    document = documents.DataDoc
    permission_classes = ()


class DataAdd(CreatedByMixin, LoggingProtectedCreateView):
    template_name = "data/add.html"
    model = models.Data
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("data:list")
    target_type = "data"

    def get_data(self):
        try:
            return self.get_object()
        except AttributeError:
            pk = self.request.GET.get("pk", None)
            try:
                return models.Data.objects.get(pk=pk)
            except models.Data.ObjectDoesNotExist:
                return

    def get_initial(self):
        data = None
        try:
            data = self.get_data()
        except Exception:
            pass
        if not data:
            return super().get_initial()

        initial_data = super().get_initial()
        for field in [
            "name",
            "note",
            "update_frequency",
            "area",
            "start_time_coverage",
            "end_time_coverage",
            "timeliness",
            "data_policy",
            "data_type",
            "data_format",
            "quality_control_procedure",
            "status",
            "dissemination",
        ]:
            initial_data[field] = getattr(data, field)
        initial_data["inspire_themes"] = getattr(data, "inspire_themes").all()
        initial_data["geographical_coverage"] = getattr(
            data, "geographical_coverage"
        ).all()
        return initial_data.copy()

    def get_form_class(self):
        data = None
        try:
            data = self.get_data()
        except Exception:
            pass
        if data:
            self.post_action = "cloned data {pk} to".format(pk=data.pk)
            self.post_action_failed = "tried to clone data {pk} of".format(pk=data.pk)

            if "ready" in self.request.GET:
                return forms.DataReadyCloneForm
            return forms.DataCloneForm
        if "ready" in self.request.GET:
            return forms.DataReadyForm
        return forms.DataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (
            self.get_form_class() == forms.DataReadyForm
            or self.get_form_class() == forms.DataReadyCloneForm
        ):
            context["ready_form"] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The data were created successfully!")
        return response

    def get_success_url(self):
        instance = self.object
        return reverse("data:detail", kwargs={"pk": instance.pk})


class DataEdit(LoggingProtectedUpdateView):
    template_name = "data/edit.html"
    model = models.Data
    context_object_name = "data"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("data:list")
    target_type = "data"

    def get_form_class(self):
        if "ready" in self.request.GET:
            return forms.DataReadyForm
        return forms.DataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_form_class() == forms.DataReadyForm:
            context["ready_form"] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The data were updated successfully!")
        return response

    def get_success_url(self):
        return reverse("data:detail", kwargs={"pk": self.object.pk})


class DataDetail(ProtectedDetailView):
    template_name = "data/detail.html"
    model = models.Data
    context_object_name = "data"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")
    target_type = "data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = {
            "id": self.object.id,
            "name": self.object.name,
            "note": self.object.note,
            "update_frequency": self.object.update_frequency_id,
            "area": self.object.area_id,
            "start_time_coverage": self.object.start_time_coverage,
            "end_time_coverage": self.object.end_time_coverage,
            "timeliness": self.object.timeliness_id,
            "data_policy": self.object.data_policy_id,
            "data_type": self.object.data_type_id,
            "data_format": self.object.data_format_id,
            "feedback": self.object.feedback,
            "quality_control_procedure": self.object.quality_control_procedure_id,
            "dissemination": self.object.dissemination_id,
            "inspire_themes": [
                inspire_theme.id for inspire_theme in self.object.inspire_themes.all()
            ],
            "geographical_coverage": [
                geographical_coverage
                for geographical_coverage in self.object.geographical_coverage.all()
            ],
        }
        form = forms.DataReadyForm(data)
        context["user_groups"] = self.request.user.groups.values_list(
            "name", flat=True
        )
        if not form.is_valid():
            context["failed_validation"] = True
        return context

    def get_object(self):
        if hasattr(self, "object"):
            return self.object
        else:
            self.object = (
                self.model.objects.select_related(
                    "update_frequency",
                    "area",
                    "timeliness",
                    "data_policy",
                    "data_type",
                    "data_format",
                    "quality_control_procedure",
                    "dissemination",
                    "status",
                    "created_by",
                )
                .prefetch_related(
                    "inspire_themes",
                    "geographical_coverage",
                    "datarequirement_set",
                    "datarequirement_set__requirement",
                    "datarequirement_set__level_of_compliance",
                    "datarequirement_set__created_by",
                    "dataproviderrelation_set",
                    "dataproviderrelation_set__provider",
                    "dataproviderrelation_set__created_by",
                )
                .get(pk=self.kwargs["pk"])
            )
            return self.object


class DataDelete(LoggingProtectedDeleteView):
    template_name = "data/delete.html"
    form_class = forms.DataForm
    model = models.Data
    context_object_name = "data"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("data:list")
    target_type = "data"

    def get_success_url(self):
        messages.success(self.request, "The data were deleted successfully!")
        return reverse("data:list")


class DataTransition(ChangesRequestedMailMixin, LoggingTransitionProtectedDetailView):
    model = models.Data
    template_name = "data/transition.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    context_object_name = "data"
    target_type = "data"

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
        data = self.get_object(self.get_queryset())
        return reverse("data:detail", kwargs={"pk": data.pk})

    def post(self, request, *args, **kwargs):
        data = self.get_object(self.get_queryset())
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition_name = self.kwargs.get("transition")

        transition = getattr(data, transition_name, None)
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
        data.requesting_user = self.request.user
        transition()
        data.save()
        feedback = ""
        if transition_name == "request_changes":
            data.feedback = ""
            data.feedback = request.POST.get("feedback", "")
            data.save()
            feedback = request.POST.get("feedback", "")
            self.send_mail(data, data.name, feedback)
        return HttpResponseRedirect(reverse("data:detail", kwargs={"pk": data.pk}))
        raise Http404()


class DataClearFeedback(LoggingProtectedCreateView):
    model = models.Data
    context_object_name = "data"
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("data:list")
    target_type = "data"

    def post(self, request, *args, **kwargs):
        data = self.get_object(self.get_queryset())
        data.feedback = ""
        data.save()
        return HttpResponseRedirect(reverse("data:detail", kwargs={"pk": data.pk}))
