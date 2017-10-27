from django.core.urlresolvers import reverse, reverse_lazy

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView, CreatedByMixin
from insitu.views.protected import (
    ProtectedTemplateView, ProtectedDetailView,
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from insitu.views.protected import IsAuthenticated, IsCopernicusServiceResponsible
from picklists import models as pickmodels


class DataList(ProtectedTemplateView):
    template_name = 'data/list.html'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_context_data(self):
        context = super(DataList, self).get_context_data()
        update_frequencies = get_choices('name',
                                         model_cls=pickmodels.UpdateFrequency)
        coverages = get_choices('name', model_cls=pickmodels.Coverage)
        timelinesses = get_choices('name', model_cls=pickmodels.Timeliness)
        policies = get_choices('name', model_cls=pickmodels.Policy)
        data_types = get_choices('name', model_cls=pickmodels.DataType)
        data_formats = get_choices('name', model_cls=pickmodels.DataFormat)
        quality_control_procedures = get_choices(
            'name',
            model_cls=pickmodels.QualityControlProcedure
        )
        disseminations = get_choices('name', model_cls=pickmodels.Dissemination)
        context.update({
            'update_frequencies': update_frequencies,
            'coverages': coverages,
            'timelinesses': timelinesses,
            'policies': policies,
            'data_types': data_types,
            'data_formats': data_formats,
            'quality_control_procedures': quality_control_procedures,
            'disseminations': disseminations,
        })
        return context


class DataListJson(ESDatatableView):
    columns = ['name', 'update_frequency', 'coverage', 'timeliness', 'policy',
               'data_type', 'data_format', 'quality_control_procedure',
               'dissemination']
    order_columns = columns
    filters = ['update_frequency', 'coverage', 'timeliness', 'policy',
               'data_type', 'data_format', 'quality_control_procedure',
               'dissemination']
    document = documents.DataDoc
    permission_classes = (IsAuthenticated, )


class DataAdd(CreatedByMixin, ProtectedCreateView):
    template_name = 'data/add.html'
    form_class = forms.DataForm
    model = models.Data
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')

    def get_success_url(self):
        instance = self.object
        return reverse('data:detail', kwargs={'pk': instance.pk})


class DataEdit(ProtectedUpdateView):
    template_name = 'data/edit.html'
    form_class = forms.DataForm
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')

    def get_success_url(self):
        return reverse('data:detail', kwargs={'pk': self.object.pk})


class DataDetail(ProtectedDetailView):
    template_name = 'data/detail.html'
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('auth:login')


class DataDelete(ProtectedDeleteView):
    template_name = 'data/delete.html'
    form_class = forms.DataForm
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsCopernicusServiceResponsible,)
    permission_denied_redirect = reverse_lazy('data:list')

    def get_success_url(self):
        return reverse('data:list')
