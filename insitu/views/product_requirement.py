# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from insitu import models
from insitu import forms


class ProductRequirementAdd(CreateView):
    template_name = 'product/requirement/add.html'
    form_class = forms.ProductRequirementForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_pk = self.kwargs['product_pk']
        context['product'] = models.Product.objects.get(pk=product_pk)
        return context

    def get_success_url(self):
        return reverse('product:detail',
                       kwargs={'pk': self.kwargs['product_pk']})


class ProductRequirementEdit(UpdateView):
    model = models.ProductRequirement
    template_name = 'product/requirement/edit.html'
    form_class = forms.ProductRequirementForm
    context_object_name = 'rel'

    def get_success_url(self):
        return reverse('product:detail',
                       kwargs={'pk': self.kwargs['product_pk']})


class ProductRequirementDelete(DeleteView):
    model = models.ProductRequirement
    template_name = 'product/requirement/delete.html'
    form_class = forms.ProductRequirementForm
    context_object_name = 'rel'

    def get_success_url(self):
        return reverse('product:detail',
                       kwargs={'pk': self.kwargs['product_pk']})
