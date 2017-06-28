# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from insitu import models
from insitu import forms


class ProductRequirementAdd(CreateView):
    template_name = 'product/requirement/add.html'
    form_class = forms.ProductRequirementForm

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields['product'].initial = self.kwargs['product_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_pk = self.kwargs['product_pk']
        context['product'] = models.Product.objects.get(pk=product_pk)
        context['title'] = (
            "Add a new requirement for " + context['product'].name
        )
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse('product:detail',
                       kwargs={'pk': self.kwargs['product_pk']})


class ProductRequirementEdit(UpdateView):
    model = models.ProductRequirement
    template_name = 'product/requirement/edit.html'
    form_class = forms.ProductRequirementEditForm
    context_object_name = 'rel'

    def _get_reverse_url(self):
        if 'product_pk' in self.kwargs:
            url = reverse('product:detail',
                       kwargs={'pk': self.kwargs['product_pk']})
        else:
            url = reverse('requirement:detail',
                       kwargs={'pk': self.kwargs['requirement_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()


class ProductRequirementDelete(DeleteView):
    model = models.ProductRequirement
    template_name = 'product/requirement/delete.html'
    form_class = forms.ProductRequirementEditForm
    context_object_name = 'rel'

    def _get_reverse_url(self):
        if 'product_pk' in self.kwargs:
            url = reverse('product:detail',
                          kwargs={'pk': self.kwargs['product_pk']})
        else:
            url = reverse('requirement:detail',
                          kwargs={'pk': self.kwargs['requirement_pk']})
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self._get_reverse_url()
        return context

    def get_success_url(self):
        return self._get_reverse_url()
