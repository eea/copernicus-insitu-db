# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages

from insitu.views.base import CreatedByMixin
from insitu.views.protected import (
    IsAuthenticated,
    IsDraftObject,
    IsNotReadOnlyUser,
    IsOwnerUser,
)
from django.urls import reverse_lazy

from insitu.views.protected import (
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView
)

from insitu import models
from insitu import forms


class DataDataProviderAdd(CreatedByMixin, LoggingProtectedCreateView):
    template_name = 'data/data_provider/add.html'
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy('data:list')
    form_class = forms.DataProviderRelationGroupForm
    form_field = 'data'
    model = models.Data
    title = "Add a new provider for {}"
    target_type = 'relation between data and data provider'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The relation between data and data provider was created successfully!')
        return response

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.kwargs['group_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(pk=self.kwargs['group_pk'])
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})


class DataDataProviderEdit(LoggingProtectedUpdateView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/edit.html'
    form_class = forms.DataProviderRelationEditForm
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'relation between data and data provider'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The relation between data and data provider was updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})


class DataDataProviderDelete(LoggingProtectedDeleteView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'relation between data and data provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        if self.request.method != 'GET':
            messages.success(self.request, 'The relation between data and data provider was deleted successfully!')
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})
