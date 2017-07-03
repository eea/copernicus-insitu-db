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

