# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from insitu import models
from insitu import forms


class RequirementProductRequirementAdd(CreateView):
    template_name = 'product/requirement/add.html'
    form_class = forms.RequirementProductRequirementForm

    def get_form(self):
        form = super().get_form(self.form_class)
        form.fields['requirement'].initial = self.kwargs['requirement_pk']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requirement_pk = self.kwargs['requirement_pk']
        context['requirement'] = (
            models.Requirement.objects.get(pk=requirement_pk)
        )
        context['url'] = self.get_success_url()
        context['title'] = (
            "Add a new product for " + context['requirement'].name
        )
        return context

    def get_success_url(self):
        return reverse('requirement:detail',
                       kwargs={'pk': self.kwargs['requirement_pk']})
