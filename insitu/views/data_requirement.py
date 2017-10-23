from django.urls import reverse_lazy

from insitu import models
from insitu import forms
from insitu.views.protected import (
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from insitu.views.protected.permissions import IsCopernicusServiceResponsible


class DataRequirementAdd(ProtectedCreateView):
    template_name = 'data/requirement/add.html'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('requirement:list')
    form_class = forms.RequirementDataRequirementForm
    form_field = 'requirement'
    model = models.Requirement
    title = "Add a new data for {}"

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.kwargs['requirement_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(
            pk=self.kwargs['requirement_pk'])
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})


class DataRequirementEdit(ProtectedUpdateView):
    model = models.DataRequirement
    template_name = 'data/requirement/edit.html'
    form_class = forms.DataRequirementEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('requirement:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})


class DataRequirementDelete(ProtectedDeleteView):
    model = models.DataRequirement
    template_name = 'data/requirement/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('requirement:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})
