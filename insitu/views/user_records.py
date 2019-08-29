from django.urls import reverse_lazy
from insitu.models import Data, DataProvider,DataProviderRelation, DataRequirement, Product, ProductRequirement, Requirement
from insitu.views import ProtectedTemplateView, IsAuthenticated


class UserRecordsView(ProtectedTemplateView):
    template_name = 'user_records.html'
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context['data_list'] = Data.objects.filter(
            created_by=current_user
        )
        context['providers_list'] = DataProvider.objects.filter(
            created_by=current_user
        )
        context['provider_relations'] = DataProviderRelation.objects.filter(
            created_by=current_user
        )
        context['data_requirements'] = DataRequirement.objects.filter(
            created_by=current_user
        )
        context['product_requirements'] = ProductRequirement.objects.filter(
            created_by=current_user
        )
        context['product_requirements'] = Requirement.objects.filter(
            created_by=current_user
        )
        context['requirements_list'] = Requirement.objects.filter(
            created_by=current_user
        )
        return context
