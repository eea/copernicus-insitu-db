from django.core.urlresolvers import reverse

from insitu import models
from insitu import forms
from insitu.views.protected import (
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from insitu.views.protected.permissions import IsCopernicusServiceResponsible


class DataRequirementAdd(ProtectedCreateView):
    template_name = 'data_group/requirement/add.html'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'data_group_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('data_group:list')
        else:
            self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def _set_model_used(self):
        if 'data_group_pk' in self.kwargs:
            self.form_class = forms.DataRequirementForm
            self.form_field = 'data_group'
            self.model = models.DataGroup
            self.title = "Add a new requirement for {}"
            self.pk = self.kwargs['data_group_pk']
        else:
            self.form_class = forms.RequirementDataRequirementForm
            self.form_field = 'requirement'
            self.model = models.Requirement
            self.title = "Add a new data_group for {}"
            self.pk = self.kwargs['requirement_pk']

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.pk
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(pk=self.pk)
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        if 'data_group_pk' in self.kwargs:
            return reverse('data_group:detail',
                           kwargs={'pk': self.kwargs['data_group_pk']})
        else:
            return reverse('requirement:detail',
                           kwargs={'pk': self.kwargs['requirement_pk']})

    def get(self, request, *args, **kwargs):
        self._set_model_used()
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_model_used()
        return super().post(self, request, *args, **kwargs)


class DataRequirementEdit(ProtectedUpdateView):
    model = models.DataRequirement
    template_name = 'data_group/requirement/edit.html'
    form_class = forms.DataRequirementEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'data_group_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('data_group:list')
        else:
            self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'data_group_pk' in self.kwargs:
            url = reverse('data_group:detail',
                          kwargs={'pk': self.kwargs['data_group_pk']})
        else:
            url = reverse('requirement:detail',
                          kwargs={'pk': self.kwargs['requirement_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()


class DataRequirementDelete(ProtectedDeleteView):
    model = models.DataRequirement
    template_name = 'data_group/requirement/delete.html'
    form_class = forms.DataRequirementEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'data_group_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('data_group:list')
        else:
            self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'data_group_pk' in self.kwargs:
            url = reverse('data_group:detail',
                          kwargs={'pk': self.kwargs['data_group_pk']})
        else:
            url = reverse('requirement:detail',
                          kwargs={'pk': self.kwargs['requirement_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()
