# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from insitu import documents
from insitu import models
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
