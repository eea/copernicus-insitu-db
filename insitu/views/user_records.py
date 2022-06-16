from django.urls import reverse_lazy
from insitu.utils import export_logs_excel
from insitu.models import (
    Data,
    DataProvider,
    DataProviderRelation,
    DataRequirement,
    ProductRequirement,
    Requirement,
    User,
    LoggedAction,
)
from insitu.views import ProtectedTemplateView
from insitu.views.protected import (
    IsCurrentUser,
)
from datetime import date, datetime


class ExportLogs(ProtectedTemplateView):
    def get(self, request):
        start_date = (
            request.GET["start_date"] if request.GET["start_date"] else date.today()
        )
        end_date = (
            datetime.combine(
                datetime.strptime(request.GET["end_date"], "%Y-%m-%d").date(),
                datetime.now().time(),
            )
            if request.GET["end_date"]
            else datetime.today()
        )

        requested_user = request.GET["requested_user"]
        query = LoggedAction.objects.filter(user=requested_user).filter(
            logged_date__range=[start_date, end_date]
        )
        return export_logs_excel(query)


class UserRecordsView(ProtectedTemplateView):
    model = User
    template_name = "user_records.html"
    permission_classes = (IsCurrentUser,)
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users_list"] = User.objects.all()
        current_user = self.request.user
        context["data_list"] = Data.objects.filter(created_by=current_user)
        context["providers_list"] = DataProvider.objects.filter(created_by=current_user)
        context["provider_relations"] = DataProviderRelation.objects.filter(
            created_by=current_user
        )
        context["data_requirements"] = DataRequirement.objects.filter(
            created_by=current_user
        )
        context["product_requirements"] = ProductRequirement.objects.filter(
            created_by=current_user
        )
        context["requirements_list"] = Requirement.objects.filter(
            created_by=current_user
        )

        context["no_records"] = not any(
            [
                context["requirements_list"],
                context["data_requirements"],
                context["data_list"],
                context["providers_list"],
                context["provider_relations"],
                context["product_requirements"],
            ]
        )
        return context
