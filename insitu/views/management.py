import re
import json
import requests
from datetime import datetime
from django.urls import reverse_lazy
from django.conf import settings

from insitu.views.protected import (
    IsAuthenticated,
    IsSuperuser,
)
from insitu.views.protected.views import ProtectedTemplateView
from insitu.utils import PICKLISTS_DESCRIPTION
from picklists import models


class Manager(ProtectedTemplateView):
    template_name = 'manage.html'
    permission_classes = (IsSuperuser,)
    permission_denied_redirect = reverse_lazy('auth:login')


class HelpPage(ProtectedTemplateView):
    template_name = 'help.html'
    permission_classes = (IsAuthenticated, )
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
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')

    @staticmethod
    def get_issues(status='unresolved'):
        base_url = settings.SENTRY_BASE_URL
        endpoint = 'issues/?query=is:' + status

        url = ''.join((base_url, endpoint))
        r = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {settings.SENTRY_AUTH_TOKEN}"
            }
        )

        response = json.loads(r.text)
        issues = list()
        for message in response:
            issue = dict()

            issue['name'] = message['title']
            parsed_date = re.sub('[A-Z]', '', message['lastSeen'])
            issue['timestamp'] = datetime.strptime(parsed_date, '%Y-%m-%d%H:%M:%S.%f')
            issue['resolved'] = (message['status'] == 'resolved')

            issues.append(issue)

        return issues

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resolved = AboutView.get_issues(status='resolved')
        unresolved = AboutView.get_issues(status='unresolved')

        issues = resolved + unresolved
        issues.sort(key=lambda i: i['timestamp'], reverse=True)

        context['issues'] = issues

        return context

