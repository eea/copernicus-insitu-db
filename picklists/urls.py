from django.urls import path

from picklists import views

urlpatterns = [
    path("export", views.ExportPicklistsView.as_view(), name="export"),
    path("import", views.ImportPicklistsView.as_view(), name="import"),
]
