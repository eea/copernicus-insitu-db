from django.urls import reverse_lazy

from insitu.views import protected
from insitu.views.protected.views import ProtectedTemplateView
from picklists import models


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
            models.Barrier, models.ComplianceLevel, models.Coverage, models.Criticality,
            models.Country, models.DataFormat, models.DataType, models.DefinitionLevel,
            models.Dissemination, models.EssentialVariable, models.UpdateFrequency,
            models.InspireTheme, models.ProductGroup, models.RequirementGroup,
            models.ProductStatus, models.Relevance, models.QualityControlProcedure,
            models.Timeliness, models.Policy, models.ProviderType
        ]

        for model in PICKLISTS:
            data = {
                'nice_name': model._meta.verbose_name,
                'objects': model.objects.order_by('pk'),
                'fields': [field.name for field in model._meta.fields
                           if field.name not in ('id', 'sort_order')]
            }
            context['models'][model._meta.model_name] = data
        return context
