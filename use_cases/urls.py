from django.conf.urls import url
from use_cases import views


urlpatterns = [
    url(r"^$", views.UseCaseListView.as_view(), name="list"),
    url(r"^(?P<pk>[0-9]+)/$", views.UseCaseDetailView.as_view(), name="detail"),
    url(r"^add/$", views.UseCaseAddView.as_view(), name="add"),
]
