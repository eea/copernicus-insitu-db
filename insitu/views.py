# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, TemplateView

from django_datatables_view.base_datatable_view import BaseDatatableView

from insitu.forms import ProductForm
from insitu.documents import ProductDoc


class HomeView(TemplateView):
    template_name = 'home.html'


class ProductList(TemplateView):
    template_name = 'product_list.html'


class ProductAdd(CreateView):
    template_name = 'product_add.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse('product_list')


class ProductListJson(BaseDatatableView):
    columns = ['acronym', 'name']
    order_columns = ['acronym', 'name']

    def get_initial_queryset(self):
        return ProductDoc.search()

    def filter_queryset(self, qs):
        search_text = self.request.GET.get('search[value]', '')
        if not search_text:
            return qs
        return qs.query('query_string', query=search_text)
