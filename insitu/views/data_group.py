from django.core.urlresolvers import reverse

from django.views.generic import CreateView, DetailView, UpdateView

from insitu import forms
from insitu import models


class DataGroupAdd(CreateView):
    template_name = 'data_group/add.html'
    form_class = forms.DataGroupForm
    model = models.DataGroup

    def get_success_url(self):
        instance = self.object
        return reverse('data_group:detail', kwargs={'pk': instance.pk})


class DataGroupEdit(UpdateView):
    template_name = 'data_group/edit.html'
    form_class = forms.DataGroupForm
    model = models.DataGroup
    context_object_name = 'data_group'

    def get_success_url(self):
        return reverse('data_group:detail', kwargs={'pk': self.object.pk})


class DataGroupDetail(DetailView):
    template_name = 'data_group/detail.html'
    model = models.DataGroup
    context_object_name = 'data_group'
