from django.urls import path
from use_cases import views


urlpatterns = [
    path("", views.UseCaseListView.as_view(), name="list"),
    path("<int:pk>/", views.UseCaseDetailView.as_view(), name="detail"),
    path("add/", views.UseCaseAddView.as_view(), name="add"),
    path(
        "<int:pk>/transition/<str:source>-to-<str:target>/<slug:transition>/",
        views.UseCaseTransition.as_view(),
        name="transition",
    ),
]
