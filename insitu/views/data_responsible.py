# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from insitu import documents
from insitu import models
from insitu import forms
from insitu.utils import ALL_OPTIONS_LABEL
from insitu.views.base import ESDatatableView
from insitu.views.protected import (
    ProtectedTemplateView, ProtectedDetailView,
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from insitu.views.protected import IsAuthenticated
from insitu.views.protected.permissions import IsCopernicusServiceResponsible


class DataResponsibleList(ProtectedTemplateView):
    template_name = 'data_responsible/list.html'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_context_data(self):
        context = super().get_context_data()
        responsible_types = (
            ((0, ALL_OPTIONS_LABEL), ) +
            models.DataResponsibleDetails.TYPE_CHOICES)
        context.update({
            'ALL_OPTIONS_LABEL': ALL_OPTIONS_LABEL,
            'responsible_types': responsible_types,
        })
        return context


class DataResponsibleListJson(ESDatatableView):
    columns = ['name', 'acronym', 'address', 'phone', 'email', 'contact_person',
               'responsible_type', 'is_network']
    order_columns = columns
    filters = ['is_network', 'responsible_type']
    document = documents.DataResponsibleDoc
    permission_classes = (IsAuthenticated, )


class DataResponsibleDetail(ProtectedDetailView):
    model = models.DataResponsible
    context_object_name = 'responsible'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_template_names(self):
        responsible = self.object
        if responsible.is_network:
            return ['data_responsible/network/detail.html']
        return ['data_responsible/non_network/detail.html']


class DataResponsibleAddNetwork(ProtectedCreateView):
    template_name = 'data_responsible/network/add.html'
    form_class = forms.DataResponsibleNetworkForm
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_success_url(self):
        return reverse('responsible:detail', kwargs={'pk': self.object.pk})


class DataResponsibleEditNetwork(ProtectedUpdateView):
    template_name = 'data_responsible/network/edit.html'
    form_class = forms.DataResponsibleNetworkForm
    context_object_name = 'responsible'
    model = models.DataResponsible
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_success_url(self):
        return reverse('responsible:detail', kwargs={'pk': self.object.pk})


class DataResponsibleDeleteNetwork(ProtectedDeleteView):
    template_name = 'data_responsible/network/delete.html'
    form_class = forms.DataResponsibleNetworkForm
    context_object_name = 'responsible'
    model = models.DataResponsible
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_success_url(self):
        return reverse('responsible:list')


class DataResponsibleAddNonNetwork(ProtectedCreateView):
    template_name = 'data_responsible/non_network/add.html'
    form_class = forms.DataResponsibleNonNetworkForm
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'details' not in context:
            context['details'] = forms.DataResponsibleDetailsForm()
        return context

    def _create_objects(self, form):
        self.object = form.save()
        data = form.data.copy()
        data['data_responsible'] = self.object.pk
        details_form = forms.DataResponsibleDetailsForm(data=data)
        details_form.save()

    def form_valid(self, form):
        details_form = forms.DataResponsibleDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        self._create_objects(form)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataResponsibleDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(self.get_context_data(
            form=form,
            details=details_form))

    def get_success_url(self):
        return reverse('responsible:detail', kwargs={'pk': self.object.pk})


class DataResponsibleEditNonNetwork(ProtectedUpdateView):
    template_name = 'data_responsible/non_network/edit.html'
    form_class = forms.DataResponsibleNonNetworkForm
    context_object_name = 'responsible'
    model = models.DataResponsible
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'details' not in context:
            details = self.object.details.first()
            context['details'] = forms.DataResponsibleDetailsForm(instance=details)
        return context

    def _update_objects(self, form):
        self.object = form.save()
        details = self.object.details.first()
        data = form.data.copy()
        data['data_responsible'] = self.object.pk
        details_form = forms.DataResponsibleDetailsForm(instance=details,
                                                        data=data)
        details_form.save()

    def form_valid(self, form):
        details_form = forms.DataResponsibleDetailsForm(data=form.data)
        if not details_form.is_valid():
            return self.form_invalid(form)
        self._update_objects(form)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        details_form = forms.DataResponsibleDetailsForm(form.data)
        details_form.is_valid()
        return self.render_to_response(self.get_context_data(
            form=form,
            details=details_form))

    def get_success_url(self):
        return reverse('responsible:detail', kwargs={'pk': self.object.pk})


class DataResponsibleDeleteNonNetwork(ProtectedDeleteView):
    template_name = 'data_responsible/non_network/delete.html'
    form_class = forms.DataResponsibleNonNetworkForm
    context_object_name = 'responsible'
    model = models.DataResponsible
    permission_classes = (IsCopernicusServiceResponsible, )
    permission_denied_redirect = reverse_lazy('responsible:list')

    def get_success_url(self):
        return reverse('responsible:list')
