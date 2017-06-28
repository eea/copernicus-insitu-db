# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices, ALL_OPTIONS_LABEL
from picklists import models as pickmodels


class ProductList(TemplateView):
    template_name = 'product/list.html'

    def get_context_data(self):
        context = super(ProductList, self).get_context_data()
        services = get_choices(models.CopernicusService, 'name')
        groups = get_choices(pickmodels.ProductGroup, 'name')
        statuses = get_choices(pickmodels.ProductStatus, 'name')
        coverages = get_choices(pickmodels.Coverage, 'name')
        context.update({
            'services': services,
            'groups': groups,
            'statuses': statuses,
            'coverages': coverages,
        })
        return context


class ProductListJson(BaseDatatableView):
    columns = ['acronym', 'name', 'group', 'service', 'component', 'entity',
               'status', 'coverage']
    order_columns = columns
    filters = ['service', 'group', 'status', 'coverage']

    def get_initial_queryset(self):
        return documents.ProductDoc.search()

    def filter_queryset(self, qs):
        for filter in self.filters:
            value = self.request.GET.get(filter)
            if not value or value == ALL_OPTIONS_LABEL:
                continue
            qs = qs.filter('term', **{filter: value})

        search_text = self.request.GET.get('search[value]', '')
        if not search_text:
            return qs
        return qs.query('query_string', query=search_text)


class ProductAdd(CreateView):
    template_name = 'product/add.html'
    form_class = forms.ProductForm

    def get_success_url(self):
        return reverse('product:list')


class ProductEdit(UpdateView):
    template_name = 'product/edit.html'
    form_class = forms.ProductForm
    model = models.Product
    context_object_name = 'product'

    def get_success_url(self):
        return reverse('product:list')


class ProductDetail(DetailView):
    template_name = 'product/detail.html'
    model = models.Product
    context_object_name = 'product'
