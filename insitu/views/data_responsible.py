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
