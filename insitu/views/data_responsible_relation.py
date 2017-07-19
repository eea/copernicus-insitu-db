# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from insitu.views.protected import IsCopernicusServiceResponsible
from insitu.views.protected import (
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)

from insitu import models
from insitu import forms


class DataDataResponsibleAdd(ProtectedCreateView):
    template_name = 'data/data_responsible/add.html'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'responsible_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('responsible:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _set_model_used(self):
        if 'responsible_pk' in self.kwargs:
            self.form_class = forms.DataResponsibleRelationResponsibleForm
            self.form_field = 'responsible'
            self.model = models.DataResponsible
            self.title = "Add a new group for {}"
            self.pk = self.kwargs['responsible_pk']
        else:
            self.form_class = forms.DataResponsibleRelationGroupForm
            self.form_field = 'data'
            self.model = models.Data
            self.title = "Add a new responsible for {}"
            self.pk = self.kwargs['group_pk']

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
        if 'responsible_pk' in self.kwargs:
            return reverse('responsible:detail',
                           kwargs={'pk': self.kwargs['responsible_pk']})
        else:

            return reverse('data:detail',
                           kwargs={'pk': self.kwargs['group_pk']})

    def get(self, request, *args, **kwargs):
        self._set_model_used()
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_model_used()
        return super().post(self, request, *args, **kwargs)


class DataDataResponsibleEdit(ProtectedUpdateView):
    model = models.DataResponsibleRelation
    template_name = 'data/data_responsible/edit.html'
    form_class = forms.DataResponsibleRelationEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'responsible_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('responsible:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'responsible_pk' in self.kwargs:
            url = reverse('responsible:detail',
                       kwargs={'pk': self.kwargs['responsible_pk']})
        else:
            url = reverse('data:detail',
                       kwargs={'pk': self.kwargs['group_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()


class DataDataResponsibleDelete(ProtectedDeleteView):
    model = models.DataResponsibleRelation
    template_name = 'data/data_responsible/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        if 'responsible_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('responsible:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'responsible_pk' in self.kwargs:
            url = reverse('responsible:detail',
                          kwargs={'pk': self.kwargs['responsible_pk']})
        else:
            url = reverse('data:detail',
                          kwargs={'pk': self.kwargs['group_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()
