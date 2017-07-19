from django.conf.urls import url

from picklists import views

urlpatterns = [
    url(r'^export$',
        views.ExportPicklistsView.as_view(),
        name='export'),

    url(r'import$',
        views.ImportPicklistsView.as_view(),
        name='import')
]
