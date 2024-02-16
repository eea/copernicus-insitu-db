# Create your views here.
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.http import Http404
from django.http.response import HttpResponseRedirect
from use_cases.models import UseCase
from use_cases.forms import ReferenceFormSet, UseCaseForm
from insitu import models as copernicus_models
from insitu.views.base import ChangesRequestedMailMixin
from insitu.views.protected import (
    LoggingProtectedCreateView,
    LoggingTransitionProtectedDetailView,
    LoggingProtectedUpdateView,
    LoggingProtectedDeleteView,
    ProtectedDetailView,
    IsAuthenticated,
    IsNotReadOnlyUser,
    IsPublicbyPublishment,
)
from use_cases.permissions import UseCaseIsEditable, UseCaseIsCreator
from django_fsm import has_transition_perm
from django.db import transaction
from django.db.models import Q
from django_filters import FilterSet, CharFilter


def multiple_search(queryset, name, value):
    queryset = queryset.filter(
        Q(title__icontains=value) | Q(description__icontains=value)
    )
    return queryset


class UseCaseFilter(FilterSet):
    search = CharFilter(label="Search", method=multiple_search)

    class Meta:
        model = UseCase
        fields = ["country", "themes", "copernicus_service"]


class UseCaseListView(ListView):
    model = UseCase
    paginate_by = 12
    template_name = "usecases/list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("id")
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(state="published")
        self.filterset = UseCaseFilter(self.request.GET, queryset=queryset)

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(UseCaseListView, self).get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class UseCaseDetailView(ProtectedDetailView):
    model = UseCase
    template_name = "usecases/detail.html"
    permission_classes = (IsPublicbyPublishment,)
    permission_denied_redirect = reverse_lazy("use_cases:list")


class UseCaseAddView(LoggingProtectedCreateView):
    model = UseCase
    form_class = UseCaseForm
    template_name = "usecases/add.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("use_cases:list")
    target_type = "usecase"

    def get_context_data(self, **kwargs):
        data = super(UseCaseAddView, self).get_context_data(**kwargs)
        if self.request.POST:
            data["references"] = ReferenceFormSet(self.request.POST)
        else:
            data["references"] = ReferenceFormSet()
        data["components"] = copernicus_models.Component.objects.all()
        data["copernicus_services"] = copernicus_models.CopernicusService.objects.all()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        references = context["references"]
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()

            if references.is_valid():
                references.instance = self.object
                references.save()
        messages.success(self.request, "The use case was created successfully!")
        return super(UseCaseAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse("use_cases:detail", kwargs={"pk": self.object.pk})


class UseCaseEditView(LoggingProtectedUpdateView):
    model = UseCase
    form_class = UseCaseForm
    template_name = "usecases/edit.html"
    permission_classes = (
        IsAuthenticated,
        IsNotReadOnlyUser,
        UseCaseIsEditable,
        UseCaseIsCreator,
    )
    permission_denied_redirect = reverse_lazy("use_cases:list")
    target_type = "usecase"

    def get_context_data(self, **kwargs):
        data = super(UseCaseEditView, self).get_context_data(**kwargs)
        data["components"] = copernicus_models.Component.objects.all()
        data["copernicus_services"] = copernicus_models.CopernicusService.objects.all()
        if self.request.POST:
            data["references"] = ReferenceFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["references"] = ReferenceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        references = context["references"]
        with transaction.atomic():
            self.object = form.save(commit=True)
            if references.is_valid():
                references.save()

        messages.success(self.request, "The use case was updated successfully!")
        return super(UseCaseEditView, self).form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "The use case was not updated!")
        return response

    def get_success_url(self):
        return reverse("use_cases:detail", kwargs={"pk": self.object.pk})


class UseCaseDeleteView(LoggingProtectedDeleteView):
    template_name = "usecases/delete.html"
    model = UseCase
    permission_classes = (
        IsAuthenticated,
        IsNotReadOnlyUser,
        UseCaseIsEditable,
        UseCaseIsCreator,
    )
    permission_denied_redirect = reverse_lazy("use_cases:list")

    def get_success_url(self):
        messages.success(self.request, "The use case was deleted successfully!")
        return reverse("use_cases:list")


class UseCaseClearFeedbackView(ProtectedDetailView):
    model = UseCase
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy("use_cases:list")

    def get(self, request, *args, **kwargs):
        use_case = self.get_object()
        use_case.feedback = ""
        use_case.save()
        return HttpResponseRedirect(
            reverse("use_cases:detail", kwargs={"pk": use_case.pk})
        )


class UseCaseTransition(
    ChangesRequestedMailMixin, LoggingTransitionProtectedDetailView
):
    model = UseCase
    template_name = "usecases/transition.html"
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    context_object_name = "usecase"
    target_type = "usecase"

    def get_success_url(self, **kwargs):
        use_case = self.get_object(self.get_queryset())
        return reverse("use_cases:detail", kwargs={"pk": use_case.pk})

    def post(self, request, *args, **kwargs):
        use_case = self.get_object(self.get_queryset())
        source = self.kwargs.get("source")
        target = self.kwargs.get("target")
        transition_name = self.kwargs.get("transition")

        transition = getattr(use_case, transition_name, None)
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
        use_case.requesting_user = self.request.user
        transition()
        use_case.save()
        feedback = ""
        if transition_name == "request_changes":
            use_case.feedback = ""
            use_case.feedback = request.POST.get("feedback", "")
            use_case.save()
            feedback = request.POST.get("feedback", "")
            self.send_mail(use_case, use_case.title, feedback, notify_teammates=False)
        return HttpResponseRedirect(
            reverse("use_cases:detail", kwargs={"pk": use_case.pk})
        )
