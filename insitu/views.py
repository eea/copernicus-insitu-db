# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import (CreateView, TemplateView, DetailView, UpdateView,
                                  DeleteView)

from django_datatables_view.base_datatable_view import BaseDatatableView

from insitu import models
from insitu import forms
from insitu.documents import ProductDoc


class HomeView(TemplateView):
    template_name = 'home.html'


class ProductList(TemplateView):
    template_name = 'product_list.html'


class ProductListJson(BaseDatatableView):
    columns = ['acronym', 'name', 'group', 'service', 'component', 'entity',
               'coverage']
    order_columns = columns

    def get_initial_queryset(self):
        return ProductDoc.search()

    def filter_queryset(self, qs):
        search_text = self.request.GET.get('search[value]', '')
        if not search_text:
            return qs
        return qs.query('query_string', query=search_text)


class ProductAdd(CreateView):
    template_name = 'product_add.html'
    form_class = forms.ProductForm

    def get_success_url(self):
        return reverse('product_list')


class ProductEdit(UpdateView):
    template_name = 'product_edit.html'
    form_class = forms.ProductForm
    model = models.Product
    context_object_name = 'product'

    def get_success_url(self):
        return reverse('product_list')


class ProductDetail(DetailView):
    template_name = 'product_detail.html'
    model = models.Product
    context_object_name = 'product'


class ProductRequirementAdd(CreateView):
    template_name = 'product_requirement_add.html'
    form_class = forms.ProductRequirementForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = models.Product.objects.get(pk=self.kwargs['product_pk'])
        return context

    def get_success_url(self):
        return reverse('product_detail',
                       kwargs={'pk': self.kwargs.get['product_pk']})


class ProductRequirementEdit(UpdateView):
    model = models.ProductRequirement
    template_name = 'product_requirement_edit.html'
    form_class = forms.ProductRequirementForm
    context_object_name = 'rel'

    def get_success_url(self):
        return reverse('product_detail',
                       kwargs={'pk': self.kwargs['product_pk']})


class ProductRequirementDelete(DeleteView):
    model = models.ProductRequirement
    template_name = 'product_requirement_delete.html'
    form_class = forms.ProductRequirementForm
    context_object_name = 'rel'

    def get_success_url(self):
        return reverse('product_detail',
                       kwargs={'pk': self.kwargs['product_pk']})
