# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from insitu.views.protected import IsCopernicusServiceProvider
from insitu.views.protected import (
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)

from insitu import models
from insitu import forms


class DataDataProviderAdd(ProtectedCreateView):
    template_name = 'data/data_provider/add.html'
    permission_classes = (IsCopernicusServiceProvider, )

    def permission_denied(self, request):
        if 'provider_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('provider:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _set_model_used(self):
        if 'provider_pk' in self.kwargs:
            self.form_class = forms.DataProviderRelationProviderForm
            self.form_field = 'provider'
            self.model = models.DataProvider
            self.title = "Add a new group for {}"
            self.pk = self.kwargs['provider_pk']
        else:
            self.form_class = forms.DataProviderRelationGroupForm
            self.form_field = 'data'
            self.model = models.Data
            self.title = "Add a new provider for {}"
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
        if 'provider_pk' in self.kwargs:
            return reverse('provider:detail',
                           kwargs={'pk': self.kwargs['provider_pk']})
        else:

            return reverse('data:detail',
                           kwargs={'pk': self.kwargs['group_pk']})

    def get(self, request, *args, **kwargs):
        self._set_model_used()
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_model_used()
        return super().post(self, request, *args, **kwargs)


class DataDataProviderEdit(ProtectedUpdateView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/edit.html'
    form_class = forms.DataProviderRelationEditForm
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceProvider, )

    def permission_denied(self, request):
        if 'provider_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('provider:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'provider_pk' in self.kwargs:
            url = reverse('provider:detail',
                       kwargs={'pk': self.kwargs['provider_pk']})
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


class DataDataProviderDelete(ProtectedDeleteView):
    model = models.DataProviderRelation
    template_name = 'data/data_provider/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsCopernicusServiceProvider, )

    def permission_denied(self, request):
        if 'provider_pk' in self.kwargs:
            self.permission_denied_redirect = reverse('provider:list')
        else:
            self.permission_denied_redirect = reverse('data:list')
        return super().permission_denied(request)

    def _get_reverse_url(self):
        if 'provider_pk' in self.kwargs:
            url = reverse('provider:detail',
                          kwargs={'pk': self.kwargs['provider_pk']})
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
