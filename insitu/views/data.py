from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView, CreatedByMixin
from insitu.views.protected import (
    LoggingProtectedTemplateView, LoggingProtectedDetailView,
    LoggingProtectedUpdateView, LoggingProtectedCreateView,
    LoggingProtectedDeleteView)
from insitu.views.protected import IsAuthenticated, IsOwnerUser
from insitu.views.protected.permissions import IsDraftObject
from picklists import models as pickmodels


class DataList(LoggingProtectedTemplateView):
    template_name = 'data/list.html'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('auth:login')
    target_type = 'data'

    def get_context_data(self):
        context = super(DataList, self).get_context_data()
        update_frequencies = get_choices('name',
                                         model_cls=pickmodels.UpdateFrequency)
        areas = get_choices('name', model_cls=pickmodels.Area)
        timelinesses = get_choices('name', model_cls=pickmodels.Timeliness)
        data_policies = get_choices('name', model_cls=pickmodels.DataPolicy)
        data_types = get_choices('name', model_cls=pickmodels.DataType)
        data_formats = get_choices('name', model_cls=pickmodels.DataFormat)
        quality_control_procedures = get_choices(
            'name',
            model_cls=pickmodels.QualityControlProcedure
        )
        disseminations = get_choices('name', model_cls=pickmodels.Dissemination)
        states = [{'title': 'All', 'name': 'All'}] + [
            state for state in models.ValidationWorkflow.states]
        context.update({
            'update_frequencies': update_frequencies,
            'areas': areas,
            'timelinesses': timelinesses,
            'data_policies': data_policies,
            'data_types': data_types,
            'data_formats': data_formats,
            'quality_control_procedures': quality_control_procedures,
            'disseminations': disseminations,
            'states': states,
        })
        return context


class DataListJson(ESDatatableView):
    columns = [
        'name', 'update_frequency', 'area', 'timeliness', 'data_policy',
        'data_type', 'data_format', 'quality_control_procedure',
        'dissemination', 'state'
    ]
    order_columns = columns
    filters = [
        'update_frequency', 'area', 'timeliness', 'data_policy',
        'data_type', 'data_format', 'quality_control_procedure',
        'dissemination', 'state'
    ]
    filter_fields = [f + '__name' if f != 'state' else 'state' for f in filters]
    document = documents.DataDoc
    permission_classes = (IsAuthenticated, )


class DataAdd(CreatedByMixin, LoggingProtectedCreateView):
    template_name = 'data/add.html'
    form_class = forms.DataForm
    model = models.Data
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'data'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The data were created successfully!')
        return response

    def get_success_url(self):
        instance = self.object
        return reverse('data:detail', kwargs={'pk': instance.pk})


class DataEdit(LoggingProtectedUpdateView):
    template_name = 'data/edit.html'
    form_class = forms.DataForm
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'data'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The data were updated successfully!')
        return response

    def get_success_url(self):
        return reverse('data:detail', kwargs={'pk': self.object.pk})


class DataDetail(LoggingProtectedDetailView):
    template_name = 'data/detail.html'
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = reverse_lazy('auth:login')
    target_type = 'data'


class DataDelete(LoggingProtectedDeleteView):
    template_name = 'data/delete.html'
    form_class = forms.DataForm
    model = models.Data
    context_object_name = 'data'
    permission_classes = (IsOwnerUser, IsDraftObject)
    permission_denied_redirect = reverse_lazy('data:list')
    target_type = 'data'

    def get_success_url(self):
        messages.success(self.request, 'The data were deleted successfully!')
        return reverse('data:list')
