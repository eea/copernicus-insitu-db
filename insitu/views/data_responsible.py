# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import TemplateView, DetailView

from insitu import documents
from insitu import models
from insitu import forms
from insitu.utils import ALL_OPTIONS_LABEL
from insitu.views.base import ESDatatableView


class DataResponsibleList(TemplateView):
    template_name = 'data_responsible/list.html'

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


class DataResponsibleDetail(DetailView):
    template_name = 'data_responsible/detail.html'
    model = models.DataResponsible
    context_object_name = 'responsible'


class DataResponsibleAddNetwork(CreateView):
    template_name = 'data_responsible/add_network.html'
    form_class = forms.DataResponsibleNetworkForm

    def get_success_url(self):
        return reverse('responsible:detail', kwargs={'pk': self.object.pk})


class DataResponsibleAddNonNetwork(CreateView):
    template_name = 'data_responsible/add_non_network.html'
    form_class = forms.DataResponsibleNonNetworkForm

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
