# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import Http404
from django.http.response import HttpResponseRedirect
from use_cases.models import UseCase
from use_cases.forms import ReferenceFormSet, UseCaseForm
from insitu.views.base import ChangesRequestedMailMixin
from insitu.views.protected import (
    LoggingProtectedCreateView,
    LoggingTransitionProtectedDetailView,
    IsAuthenticated,
    IsNotReadOnlyUser,
)
from django_fsm import has_transition_perm
from django.db import transaction


class UseCaseListView(ListView):
    model = UseCase
    paginate_by = 100
    template_name = "usecases/list.html"


class UseCaseDetailView(DetailView):
    model = UseCase
    template_name = "usecases/detail.html"


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
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        references = context["references"]
        with transaction.atomic():
            self.object = form.save()

            if references.is_valid():
                references.instance = self.object
                references.save()
        return super(UseCaseAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse("use_cases:detail", kwargs={"pk": self.object.pk})


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
            self.send_mail(use_case, feedback, use_case.title)
        return HttpResponseRedirect(
            reverse("use_cases:detail", kwargs={"pk": use_case.pk})
        )
        raise Http404()
