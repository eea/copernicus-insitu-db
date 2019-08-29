from django.views.generic import TemplateView
from insitu.models import Data, DataProvider,DataProviderRelation, DataRequirement, Product, ProductRequirement, Requirement


class UserRecordsView(TemplateView):
    template_name = 'user_records.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_list'] = Data.objects.filter(created_by=self.request.user)
        return context
