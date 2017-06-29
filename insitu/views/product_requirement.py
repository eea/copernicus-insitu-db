# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from insitu import models
from insitu import forms


class ProductRequirementAdd(CreateView):
    template_name = 'product/requirement/add.html'

    def _set_model_used(self):
        if 'product_pk' in self.kwargs:
            self.form_class = forms.ProductRequirementForm
            self.form_field = 'product'
            self.model = models.Product
            self.title = "Add a new requirement for {}"
            self.pk = self.kwargs['product_pk']
        else:
            self.form_class = forms.RequirementProductRequirementForm
            self.form_field = 'requirement'
            self.model = models.Requirement
            self.title = "Add a new product for {}"
            self.pk = self.kwargs['requirement_pk']

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.pk
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(pk=self.pk)
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        if 'product_pk' in self.kwargs:
            return reverse('product:detail',
                           kwargs={'pk': self.kwargs['product_pk']})
        else:

            return reverse('requirement:detail',
                           kwargs={'pk': self.kwargs['requirement_pk']})

    def get(self, request, *args, **kwargs):
        self._set_model_used()
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._set_model_used()
        return super().post(self, request, *args, **kwargs)

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
