# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.urls import reverse_lazy

from insitu import models
from insitu import forms
from insitu.views.base import CreatedByMixin
from insitu.views.protected import (
    LoggingProtectedUpdateView,
    LoggingProtectedCreateView,
    LoggingProtectedDeleteView
)
from insitu.views.protected.permissions import (
    IsOwnerUser,
    IsDraftObject,
    IsAuthenticated
)


class BaseProductRequirementAdd(CreatedByMixin, LoggingProtectedCreateView):
    form_field = 'requirement'
    model = models.Requirement
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('requirement:list')
    message = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.message)
        return response

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields[self.form_field].initial = self.kwargs['requirement_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.form_field] = self.model.objects.get(
            pk=self.kwargs['requirement_pk'])
        context['title'] = self.title.format(context[self.form_field].name)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})


class ProductRequirementAdd(BaseProductRequirementAdd):
    template_name = 'product/requirement/add.html'
    form_class = forms.RequirementProductRequirementForm
    title = "Add a new product for {}"
    target_type = 'relation between product and requirement'
    message = 'The relation between product and requirement was updated successfully!'


class ProductGroupRequirementAdd(BaseProductRequirementAdd):
    template_name = 'product_group/requirement/add.html'
    form_class = forms.ProductGroupRequirementForm
    title = "Add a new product group for {}"
    target_type = 'relations between product group and requirement'
    message = "The relations between the product group's products and requirement were created succesfully!"

    def get_object_id(self):
        if 'product_group' in self.request.POST:
            return 'product group {0}, requirement {1}'.format(
                self.request.POST['product_group'],
                self.kwargs['requirement_pk'],
            )
        return ''


class ProductRequirementEdit(LoggingProtectedUpdateView):
    model = models.ProductRequirement
    template_name = 'product/requirement/edit.html'
    form_class = forms.ProductRequirementEditForm
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('requirement:list')
    target_type = 'relation between product and requirement'

    def form_valid(self, form):
        response = super(ProductRequirementEdit, self).form_valid(form)
        messages.success(self.request, 'The relation between product and requirement was updated successfully!')
        return response

    def get_form_kwargs(self):
        kwargs = super(ProductRequirementEdit, self).get_form_kwargs()
        kwargs.update({'url': self.kwargs[
            'pk']})  # or wherever the url parameter is coming from
        return kwargs

    def post(self, request, *args, **kwargs):
        return super(ProductRequirementEdit, self).post(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})


class ProductRequirementDelete(LoggingProtectedDeleteView):
    model = models.ProductRequirement
    template_name = 'product/requirement/delete.html'
    context_object_name = 'rel'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('requirement:list')
    target_type = 'relation between product and requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.get_success_url()
        return context

    def get_success_url(self):
        messages.success(self.request, 'The relation between product and requirement was deleted successfully!')
        return reverse_lazy('requirement:detail',
                            kwargs={'pk': self.kwargs['requirement_pk']})
