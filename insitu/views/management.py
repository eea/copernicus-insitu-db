import datetime

from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import get_object_or_404

from insitu.views import protected
from insitu.views.protected.views import ProtectedTemplateView
from insitu.utils import PICKLISTS_DESCRIPTION
from picklists import models

from explorer.exporters import get_exporter_class
from explorer.models import Query
from explorer.views import DownloadQueryView, _export


class Manager(ProtectedTemplateView):
    template_name = 'manage.html'
    permission_classes = (protected.IsSuperuser,)
    permission_denied_redirect = reverse_lazy('auth:login')


class HelpPage(ProtectedTemplateView):
    template_name = 'help.html'
    permission_classes = (protected.IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['models'] = dict()

        PICKLISTS = [
            models.Barrier, models.ComplianceLevel, models.Area,
            models.Criticality, models.Country, models.DataFormat,
            models.DataPolicy, models.DataType, models.DefinitionLevel,
            models.Dissemination, models.EssentialVariable, models.InspireTheme,
            models.ProductGroup, models.ProductStatus, models.ProviderType,
            models.Relevance, models.RequirementGroup,
            models.QualityControlProcedure, models.Timeliness,
            models.UpdateFrequency,
        ]

        for model in PICKLISTS:
            data = {
                'nice_name': model._meta.verbose_name,
                'description': PICKLISTS_DESCRIPTION.get(model.__name__, None),
                'objects': model.objects.order_by('pk'),
                'fields': [field.name for field in model._meta.fields
                           if field.name not in ('id', 'sort_order')]
            }
            context['models'][model._meta.model_name] = data
            context['email'] = settings.SUPPORT_EMAIL
        return context


class AboutView(ProtectedTemplateView):
    template_name = 'about.html'
    permission_classes = (protected.IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')


class ReportsView(ProtectedTemplateView):
    template_name = 'reports.html'
    permission_classes = (protected.IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['queries'] = Query.objects.all().values(
            'id', 'title', 'description')
        return context


class DownloadReportView(DownloadQueryView):

    def get(self, request, query_id, *args, **kwargs):
        query = get_object_or_404(Query, pk=query_id)
        format = request.GET.get('format', 'csv')
        exporter_class = get_exporter_class(format)
        file_extension = exporter_class.file_extension
        date = '_' + datetime.datetime.now().strftime('%m-%d-%Y')
        response = _export(request, query)
        response['Content-Disposition'] = (date + file_extension).join(
            response['Content-Disposition'].split(file_extension))
        return response
