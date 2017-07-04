from django.core.urlresolvers import reverse

from django.views.generic import DetailView, TemplateView
from django.views.generic import CreateView, UpdateView

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView
from picklists import models as pickmodels


class DataGroupList(TemplateView):
    template_name = 'data_group/list.html'

    def get_context_data(self):
        context = super(DataGroupList, self).get_context_data()
        frequencies = get_choices('name', model_cls=pickmodels.Frequency)
        coverages = get_choices('name', model_cls=pickmodels.Coverage)
        timelinesses = get_choices('name', model_cls=pickmodels.Timeliness)
        policies = get_choices('name', model_cls=pickmodels.Policy)
        data_types = get_choices('name', model_cls=pickmodels.DataType)
        data_formats = get_choices('name', model_cls=pickmodels.DataFormat)
        qualities = get_choices('name', model_cls=pickmodels.Quality)
        context.update({
            'frequencies': frequencies,
            'coverages': coverages,
            'timelinesses': timelinesses,
            'policies': policies,
            'data_types': data_types,
            'data_formats': data_formats,
            'qualities': qualities,
        })
        return context


class DataGroupListJson(ESDatatableView):
    columns = ['name', 'frequency', 'coverage', 'timeliness', 'policy',
               'data_type', 'data_format', 'quality']
    order_columns = columns
    filters = ['frequency', 'coverage', 'timeliness', 'policy',
               'data_type', 'data_format', 'quality']
    document = documents.DataGroupDoc


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
