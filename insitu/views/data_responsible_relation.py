# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy

from insitu.views.protected import IsCopernicusServiceResponsible
from insitu.views.protected import (
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)

from insitu import models
from insitu import forms


class DataDataResponsibleAdd(ProtectedCreateView):
    template_name = 'data/data_responsible/add.html'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')
    form_class = forms.DataResponsibleRelationGroupForm
    form_field = 'data'
    model = models.Data
    title = "Add a new responsible for {}"

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


class DataDataResponsibleEdit(ProtectedUpdateView):
    model = models.DataResponsibleRelation
    template_name = 'data/data_responsible/edit.html'
    form_class = forms.DataResponsibleRelationEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})


class DataDataResponsibleDelete(ProtectedDeleteView):
    model = models.DataResponsibleRelation
    template_name = 'data/data_responsible/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('data:detail',
                            kwargs={'pk': self.kwargs['group_pk']})
