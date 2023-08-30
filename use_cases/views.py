# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from use_cases.models import UseCase
from use_cases.forms import ReferenceFormSet, UseCaseForm
from insitu.views.base import CreatedByMixin
from insitu.views.protected import (
    LoggingProtectedCreateView,
    IsAuthenticated,
    IsNotReadOnlyUser,
)
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
