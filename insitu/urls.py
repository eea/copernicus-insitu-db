from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemap_views
from django.views.generic.base import RedirectView
from django.views.static import serve

from copernicus import settings
from insitu import views
from insitu.sitemaps import (
    ProductSitemap,
    ProductListSitemap,
    RequirementSitemap,
    RequirementListSitemap,
    DataSitemap,
    DataListSitemap,
    DataProviderSitemap,
    DataProviderListSitemap,
    AboutSitemap,
    DocsSitemap,
    HelpSitemap,
)

sitemaps = {
    "about": AboutSitemap,
    "products_list_page": ProductListSitemap,
    "requirements_list_page": RequirementListSitemap,
    "data_list_page": DataListSitemap,
    "data_providers_list_page": DataProviderListSitemap,
    "product": ProductSitemap,
    "requirement": RequirementSitemap,
    "data": DataSitemap,
    "provider": DataProviderSitemap,
    "help": HelpSitemap,
    "docs": DocsSitemap,
}

product_requirement_patterns = [
    path("add/", views.ProductRequirementAdd.as_view(), name="add"),
    path("add-group/", views.ProductGroupRequirementAdd.as_view(), name="add_group"),
    path("<int:pk>/", views.ProductRequirementEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.ProductRequirementDelete.as_view(), name="delete"),
]

product_patterns = [
    path("list/", views.ProductList.as_view(), name="list"),
    path("data/", views.ProductListJson.as_view(), name="json"),
    path("add/", views.ProductAdd.as_view(), name="add"),
    path("<int:pk>/", views.ProductDetail.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ProductEdit.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ProductDelete.as_view(), name="delete"),
    path("export", views.ExportProductView.as_view(), name="export"),
    path("import", views.ImportProductsView.as_view(), name="import"),
]

data_requirement_patterns = [
    path("add/", views.DataRequirementAdd.as_view(), name="add"),
    path("<int:pk>/", views.DataRequirementEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.DataRequirementDelete.as_view(), name="delete"),
]

requirement_patterns = [
    path("list/", views.RequirementList.as_view(), name="list"),
    path("data/", views.RequirementListJson.as_view(), name="json"),
    path("<int:pk>/", views.RequirementDetail.as_view(), name="detail"),
    path("<int:pk>/edit/", views.RequirementEdit.as_view(), name="edit"),
    path("<int:pk>/delete/", views.RequirementDelete.as_view(), name="delete"),
    path(
        "<int:pk>/transition/<str:source>-to-<str:target>/<slug:transition>/",
        views.RequirementTransition.as_view(),
        name="transition",
    ),
    path(
        "<int:requirement_pk>/product/",
        include((product_requirement_patterns, "insitu"), namespace="product"),
    ),
    path("add/", views.RequirementAdd.as_view(), name="add"),
    path(
        "<int:requirement_pk>/data/",
        include((data_requirement_patterns, "insitu"), namespace="data"),
    ),
    path(
        "<int:pk>/clear_feedback/",
        views.RequirementClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

data_data_provider_patterns = [
    path("add/", views.DataDataProviderAdd.as_view(), name="add"),
    path("<int:pk>/", views.DataDataProviderEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.DataDataProviderDelete.as_view(), name="delete"),
]


data_patterns = [
    path("list/", views.DataList.as_view(), name="list"),
    path("data/", views.DataListJson.as_view(), name="json"),
    path("add/", views.DataAdd.as_view(), name="add"),
    path("<int:pk>/", views.DataDetail.as_view(), name="detail"),
    path("<int:pk>/edit", views.DataEdit.as_view(), name="edit"),
    path("<int:pk>/delete/", views.DataDelete.as_view(), name="delete"),
    path(
        "<int:group_pk>/provider/",
        include((data_data_provider_patterns, "insitu"), namespace="provider"),
    ),
    path(
        "<int:pk>/transition/<str:source>-to-<str:target>/<slug:transition>/",
        views.DataTransition.as_view(),
        name="transition",
    ),
    path(
        "<int:pk>/clear_feedback/",
        views.DataClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

provider_patterns = [
    path("list/", views.DataProviderList.as_view(), name="list"),
    path("list/json/", views.DataProviderListApiView.as_view(), name="list_json"),
    path("data/", views.DataProviderListJson.as_view(), name="json"),
    path("<int:pk>/", views.DataProviderDetail.as_view(), name="detail"),
    path("add-network/", views.DataProviderAddNetwork.as_view(), name="add_network"),
    path(
        "<int:pk>/edit-network/",
        views.DataProviderEditNetwork.as_view(),
        name="edit_network",
    ),
    path(
        "<int:pk>/edit-network-members/",
        views.DataProviderEditNetworkMembers.as_view(),
        name="edit_network_members",
    ),
    path(
        "<int:pk>/delete-network/",
        views.DataProviderDeleteNetwork.as_view(),
        name="delete_network",
    ),
    path("add/", views.DataProviderAddNonNetwork.as_view(), name="add_non_network"),
    path(
        "<int:pk>//edit/",
        views.DataProviderEditNonNetwork.as_view(),
        name="edit_non_network",
    ),
    path(
        "<int:pk>/delete/",
        views.DataProviderDeleteNonNetwork.as_view(),
        name="delete_non_network",
    ),
    path(
        "<int:pk>/transition/<str:source>-to-<str:target>/<slug:transition>/",
        views.DataProviderTransition.as_view(),
        name="transition",
    ),
    path(
        "<int:pk>/clear_feedback/",
        views.DataProviderClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

auth_patterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("edit_teammates/", views.EditTeamMatesView.as_view(), name="edit_teammates"),
    path(
        "transfer_ownership/",
        views.TransferOwnership.as_view(),
        name="transfer_ownership",
    ),
    path(
        "accept_teammate_request/<int:sender_user>",
        views.AcceptTeammateRequestView.as_view(),
        name="accept_request",
    ),
    path(
        "delete_teammate/<int:teammate_id>",
        views.DeleteTeammateView.as_view(),
        name="delete_teammate",
    ),
]

reports_patterns = [
    path("list/", views.ReportsListView.as_view(), name="list"),
    path(
        "standard_report/",
        views.StandardReportView.as_view(),
        name="standard_report",
    ),
    path(
        "data_providers_network/",
        views.DataProvidersNetworkReportView.as_view(),
        name="data_providers_network_report",
    ),
    path(
        "entries_count_report/",
        views.EntriesCountReportView.as_view(),
        name="entries_count_report",
    ),
    path(
        "entries_state_report/",
        views.EntriesStateReportView.as_view(),
        name="entries_state_report",
    ),
    path("country_report/", views.CountryReportView.as_view(), name="country_report"),
    path(
        "data_provider_duplicates_report/",
        views.DataProviderDuplicatesReportView.as_view(),
        name="data_provider_duplicates_report",
    ),
    path(
        "user_actions/",
        views.UserActionsReportView.as_view(),
        name="user_actions_report",
    ),
    path("snapshot/", views.SnapshotView.as_view(), name="snapshot"),
    path("<query_id>/", views.ReportsDetailView.as_view(), name="detail"),
    path("<query_id>/json/", views.ReportDataJsonView.as_view(), name="json"),
    path(
        "<query_id>/download/",
        views.DownloadReportsView.as_view(),
        name="download",
    ),
    path("schema/", RedirectView.as_view(pattern_name="explorer_schema")),
    path("report/pdf/", views.HTMLToPDFView.as_view(), name="report_pdf"),
]

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", RedirectView.as_view(url="/about")),
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("product/", include((product_patterns, "insitu"), namespace="product")),
    path(
        "requirement/",
        include((requirement_patterns, "insitu"), namespace="requirement"),
    ),
    path("data/", include((data_patterns, "insitu"), namespace="data")),
    path("provider/", include((provider_patterns, "insitu"), namespace="provider")),
    path("", include((auth_patterns, "insitu"), namespace="auth")),
    path("reports/", include((reports_patterns, "insitu"), namespace="reports")),
    path("manage", views.Manager.as_view(), name="manage"),
    path("help", views.HelpPage.as_view(), name="help"),
    path("about", views.AboutView.as_view(), name="about"),
    re_path("docs/(?P<path>.*)", serve, {"document_root": settings.DOCS_ROOT}),
    path(
        "docs/guide.html",
        serve,
        {"document_root": settings.DOCS_ROOT},
        name="user_manual",
    ),
    path("crashme", views.Crashme.as_view(), name="crashme"),
    path(
        "user/records/",
        views.UserRecordsView.as_view(),
        name="user_records",
    ),
    path(
        "user/logs",
        views.ExportLogs.as_view(),
        name="export_logs",
    ),
    path(
        "user/change_name",
        views.ChangeNameEmail.as_view(),
        name="change_name_email",
    ),
]
