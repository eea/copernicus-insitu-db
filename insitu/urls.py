from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.views.static import serve

from copernicus import settings
from insitu import views


product_requirement_patterns = [
    url(r"^add/$", views.ProductRequirementAdd.as_view(), name="add"),
    url(r"^add-group/$", views.ProductGroupRequirementAdd.as_view(), name="add_group"),
    url(r"^(?P<pk>[0-9]+)/$", views.ProductRequirementEdit.as_view(), name="edit"),
    url(
        r"^(?P<pk>[0-9]+)/delete$",
        views.ProductRequirementDelete.as_view(),
        name="delete",
    ),
]

product_patterns = [
    url(r"^list/$", views.ProductList.as_view(), name="list"),
    url(r"^data/$", views.ProductListJson.as_view(), name="json"),
    url(r"^add/$", views.ProductAdd.as_view(), name="add"),
    url(r"^(?P<pk>[0-9]+)/$", views.ProductDetail.as_view(), name="detail"),
    url(r"^(?P<pk>[0-9]+)/edit/$", views.ProductEdit.as_view(), name="edit"),
    url(r"^(?P<pk>[0-9]+)/delete/$", views.ProductDelete.as_view(), name="delete"),
    url(r"^export$", views.ExportProductView.as_view(), name="export"),
    url(r"import$", views.ImportProductsView.as_view(), name="import"),
]

data_requirement_patterns = [
    url(r"^add/$", views.DataRequirementAdd.as_view(), name="add"),
    url(r"^(?P<pk>[0-9]+)/$", views.DataRequirementEdit.as_view(), name="edit"),
    url(
        r"^(?P<pk>[0-9]+)/delete$", views.DataRequirementDelete.as_view(), name="delete"
    ),
]

requirement_patterns = [
    url(r"^list/$", views.RequirementList.as_view(), name="list"),
    url(r"^data/$", views.RequirementListJson.as_view(), name="json"),
    url(r"^(?P<pk>[0-9]+)/$", views.RequirementDetail.as_view(), name="detail"),
    url(r"^(?P<pk>[0-9]+)/edit$", views.RequirementEdit.as_view(), name="edit"),
    url(r"^(?P<pk>[0-9]+)/delete/$", views.RequirementDelete.as_view(), name="delete"),
    url(
        r"^(?P<pk>[0-9]+)/transition/(?P<source>[a-z]+)-to-(?P<target>[a-z]+)/$",
        views.RequirementTransition.as_view(),
        name="transition",
    ),
    url(
        r"^(?P<requirement_pk>[0-9]+)/product/",
        include(product_requirement_patterns, namespace="product"),
    ),
    url(r"^add/$", views.RequirementAdd.as_view(), name="add"),
    url(
        r"^(?P<requirement_pk>[0-9]+)/data/",
        include(data_requirement_patterns, namespace="data"),
    ),
    url(
        r"^(?P<pk>[0-9]+)/clear_feedback/$",
        views.RequirementClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

data_data_provider_patterns = [
    url(r"^add/$", views.DataDataProviderAdd.as_view(), name="add"),
    url(r"^(?P<pk>[0-9]+)/$", views.DataDataProviderEdit.as_view(), name="edit"),
    url(
        r"^(?P<pk>[0-9]+)/delete$",
        views.DataDataProviderDelete.as_view(),
        name="delete",
    ),
]


data_patterns = [
    url(r"^list/$", views.DataList.as_view(), name="list"),
    url(r"^data/$", views.DataListJson.as_view(), name="json"),
    url(r"^add/$", views.DataAdd.as_view(), name="add"),
    url(r"^(?P<pk>[0-9]+)/$", views.DataDetail.as_view(), name="detail"),
    url(r"^(?P<pk>[0-9]+)/edit$", views.DataEdit.as_view(), name="edit"),
    url(r"^(?P<pk>[0-9]+)/delete/$", views.DataDelete.as_view(), name="delete"),
    url(
        r"^(?P<group_pk>[0-9]+)/provider/",
        include(data_data_provider_patterns, namespace="provider"),
    ),
    url(
        r"^(?P<pk>[0-9]+)/transition/(?P<source>[a-z]+)-to-(?P<target>[a-z]+)/$",
        views.DataTransition.as_view(),
        name="transition",
    ),
    url(
        r"^(?P<pk>[0-9]+)/clear_feedback/$",
        views.DataClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

provider_patterns = [
    url(r"^list/$", views.DataProviderList.as_view(), name="list"),
    url(r"^data/$", views.DataProviderListJson.as_view(), name="json"),
    url(r"^(?P<pk>[0-9]+)/$", views.DataProviderDetail.as_view(), name="detail"),
    url(r"^add-network/$", views.DataProviderAddNetwork.as_view(), name="add_network"),
    url(
        r"^(?P<pk>[0-9]+)/edit-network/$",
        views.DataProviderEditNetwork.as_view(),
        name="edit_network",
    ),
    url(
        r"^(?P<pk>[0-9]+)/edit-network-members/$",
        views.DataProviderEditNetworkMembers.as_view(),
        name="edit_network_members",
    ),
    url(
        r"^(?P<pk>[0-9]+)/delete-network/$",
        views.DataProviderDeleteNetwork.as_view(),
        name="delete_network",
    ),
    url(r"^add/$", views.DataProviderAddNonNetwork.as_view(), name="add_non_network"),
    url(
        r"^(?P<pk>[0-9]+)/edit/$",
        views.DataProviderEditNonNetwork.as_view(),
        name="edit_non_network",
    ),
    url(
        r"^(?P<pk>[0-9]+)/delete/$",
        views.DataProviderDeleteNonNetwork.as_view(),
        name="delete_non_network",
    ),
    url(
        r"^(?P<pk>[0-9]+)/transition/(?P<source>[a-z]+)-to-(?P<target>[a-z]+)/$",
        views.DataProviderTransition.as_view(),
        name="transition",
    ),
    url(
        r"^(?P<pk>[0-9]+)/clear_feedback/$",
        views.DataProviderClearFeedback.as_view(),
        name="clear_feedback",
    ),
]

auth_patterns = [
    url(r"^login/", views.LoginView.as_view(), name="login"),
    url(r"^logout/", views.LogoutView.as_view(), name="logout"),
    url(
        r"^change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    url(r"^edit_teammates/", views.EditTeamMatesView.as_view(), name="edit_teammates"),
    url(
        r"^accept_teammate_request/(?P<sender_user>[0-9]+)",
        views.AcceptTeammateRequestView.as_view(),
        name="accept_request",
    ),
    url(
        r"^delete_teammate/(?P<teammate_id>[0-9]+)",
        views.DeleteTeammateView.as_view(),
        name="delete_teammate",
    ),
]

reports_patterns = [
    url(r"^list/$", views.ReportsListView.as_view(), name="list"),
    url(
        r"^standard_report/$",
        views.ReportsStandardReportView.as_view(),
        name="standard_report",
    ),
    url(r"^(?P<query_id>\d+)/$", views.ReportsDetailView.as_view(), name="detail"),
    url(r"^(?P<query_id>\d+)/json/$", views.ReportDataJsonView.as_view(), name="json"),
    url(r"^snapshot/$", views.SnapshotView.as_view(), name="snapshot"),
    url(r"^playground/$", views.PlaygroundView.as_view(), name="playground"),
    url(
        r"^(?P<query_id>\d+)/download/$",
        views.DownloadReportsView.as_view(),
        name="download",
    ),
    url(r"^schema/$", RedirectView.as_view(pattern_name="explorer_schema")),
    url(r"^report/pdf/$", views.Pdf.as_view(), name="report_pdf"),
]

urlpatterns = [
    url(r"^$", views.HomeView.as_view(), name="home"),
    url(
        r"^password/reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html"
        ),
        name="password_reset",
    ),
    url(
        r"^password_reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    url(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-"
        r"[0-9A-Za-z]{1,20})/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    url(
        r"^reset/done/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    url(r"^product/", include(product_patterns, namespace="product")),
    url(r"^requirement/", include(requirement_patterns, namespace="requirement")),
    url(r"^data/", include(data_patterns, namespace="data")),
    url(r"^provider/", include(provider_patterns, namespace="provider")),
    url(r"", include(auth_patterns, namespace="auth")),
    url(r"^reports/", include(reports_patterns, namespace="reports")),
    url(r"manage$", views.Manager.as_view(), name="manage"),
    url(r"help$", views.HelpPage.as_view(), name="help"),
    url(r"about$", views.AboutView.as_view(), name="about"),
    url(r"^docs/(?P<path>.*)$", serve, {"document_root": settings.DOCS_ROOT}),
    url(
        r"^docs/guide.html",
        serve,
        {"document_root": settings.DOCS_ROOT},
        name="user_manual",
    ),
    url(r"crashme$", views.Crashme.as_view(), name="crashme"),
    url(
        r"^user/(?P<pk>\d+)/records$",
        views.UserRecordsView.as_view(),
        name="user_records",
    ),
]
