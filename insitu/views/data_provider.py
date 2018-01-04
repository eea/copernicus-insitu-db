# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from insitu import documents
from insitu import models
from insitu import forms
from insitu.views.base import ESDatatableView, CreatedByMixin
from insitu.views.protected import ProtectedUpdateView
from insitu.views.protected import (
    LoggingProtectedTemplateView, LoggingProtectedDetailView,
    LoggingProtectedUpdateView, LoggingProtectedCreateView,
    LoggingProtectedDeleteView)
from insitu.views.protected import IsAuthenticated
from insitu.views.protected.permissions import (
    IsOwnerUser,
    IsDraftObject
)
from insitu.utils import get_choices

from picklists import models as pickmodels


class DataProviderList(LoggingProtectedTemplateView):
    template_name = 'data_provider/list.html'
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')
    target_type = 'data providers'

    def get_context_data(self):
        context = super().get_context_data()
        provider_types = get_choices(
            'name', model_cls=pickmodels.ProviderType)
        states = [{'title': 'All', 'name': 'All'}] + [
            state for state in models.ValidationWorkflow.states]
        context.update({
            'provider_types': provider_types,
            'states': states,
        })
        return context


class DataProviderListJson(ESDatatableView):
    columns = ['name', 'acronym', 'address', 'phone', 'email', 'contact_person',
               'provider_type', 'is_network', 'state']
    order_columns = columns
    filters = ['is_network', 'provider_type', 'state']
    document = documents.DataProviderDoc
    permission_classes = (IsAuthenticated,)


class DataProviderDetail(LoggingProtectedDetailView):
    model = models.DataProvider
    context_object_name = 'provider'
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider'

    def get_template_names(self):
        provider = self.object
        if provider.is_network:
            return ['data_provider/network/detail.html']
        return ['data_provider/non_network/detail.html']


class DataProviderAddNetwork(CreatedByMixin, LoggingProtectedCreateView):
    template_name = 'data_provider/network/add.html'
    form_class = forms.DataProviderNetworkForm
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider network'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The data provider network was created successfully!')
        return response

    def get_success_url(self):
        return reverse('provider:detail', kwargs={'pk': self.object.pk})


class DataProviderEditNetwork(LoggingProtectedUpdateView):
    template_name = 'data_provider/network/edit.html'
    form_class = forms.DataProviderNetworkForm
    context_object_name = 'provider'
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider network'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The data provider network was updated successfully!')
        return response

    def get_success_url(self):
        return reverse('provider:detail', kwargs={'pk': self.object.pk})


class DataProviderEditNetworkMembers(ProtectedUpdateView):
    template_name = 'data_provider/network/edit_members.html'
    form_class = forms.DataProviderNetworkMembersForm
    context_object_name = 'provider'
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('provider:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The members for this data provider network were updated successfully!')
        return response

    def get_success_url(self):
        return reverse('provider:detail', kwargs={'pk': self.object.pk})


class DataProviderDeleteNetwork(LoggingProtectedDeleteView):
    template_name = 'data_provider/network/delete.html'
    form_class = forms.DataProviderNetworkForm
    context_object_name = 'provider'
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider network'

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        messages.success(self.request, 'The data provider network was deleted successfully!')
        return reverse('provider:list')


class DataProviderAddNonNetwork(CreatedByMixin, LoggingProtectedCreateView):
    template_name = 'data_provider/non_network/add.html'
    form_class = forms.DataProviderNonNetworkForm
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'details' not in context:
            context['details'] = forms.DataProviderDetailsForm()
        return context

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        super().form_valid(form)
        data = form.data.copy()
        data['data_provider'] = self.object.pk
        details_form = forms.DataProviderDetailsForm(data=data)
        details_form.save(created_by=self.object.created_by)
        messages.success(self.request, 'The data provider was created successfully!')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(self.get_context_data(
            form=form,
            details=details_form))

    def get_success_url(self):
        return reverse('provider:detail', kwargs={'pk': self.object.pk})


class DataProviderEditNonNetwork(LoggingProtectedUpdateView):
    template_name = 'data_provider/non_network/edit.html'
    form_class = forms.DataProviderNonNetworkForm
    context_object_name = 'provider'
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'details' not in context:
            details = self.object.details.first()
            context['details'] = forms.DataProviderDetailsForm(instance=details)
        return context

    def _update_objects(self, form):
        self.object = form.save()
        details = self.object.details.first()
        data = form.data.copy()
        data['data_provider'] = self.object.pk
        details_form = forms.DataProviderDetailsForm(instance=details,
                                                     data=data)
        details_form.save()

    def form_valid(self, form):
        details_form = forms.DataProviderDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        self._update_objects(form)
        messages.success(self.request, 'The data provider was updated successfully!')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataProviderDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(self.get_context_data(
            form=form,
            details=details_form))

    def get_success_url(self):
        return reverse('provider:detail', kwargs={'pk': self.object.pk})


class DataProviderDeleteNonNetwork(LoggingProtectedDeleteView):
    template_name = 'data_provider/non_network/delete.html'
    form_class = forms.DataProviderNonNetworkForm
    context_object_name = 'provider'
    model = models.DataProvider
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('provider:list')
    target_type = 'data provider'

    def get_success_url(self):
        messages.success(self.request, 'The data provider was deleted successfully!')
        return reverse('provider:list')
