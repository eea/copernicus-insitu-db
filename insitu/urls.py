from django.conf.urls import url, include

from insitu import views


product_requirement_patterns = [
    url(r'^add/$',
        views.ProductRequirementAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.ProductRequirementEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        views.ProductRequirementDelete.as_view(),
        name='delete'),
]

product_patterns = [
    url(r'^list/$',
        views.ProductList.as_view(),
        name='list'),

    url(r'^filter/components/$',
        views.ComponentsFilter.as_view(),
        name='filter_components'),

    url(r'^data/$',
        views.ProductListJson.as_view(),
        name='json'),

    url(r'^add/$',
        views.ProductAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.ProductDetail.as_view(),
        name='detail'),

    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.ProductEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.ProductDelete.as_view(),
        name='delete'),

    url(r'^(?P<product_pk>[0-9]+)/requirement/',
        include(product_requirement_patterns,
                namespace='requirement')),
]

data_requirement_patterns = [
    url(r'^add/$',
        views.DataRequirementAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataRequirementEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        views.DataRequirementDelete.as_view(),
        name='delete'),
]

requirement_patterns = [
    url(r'^list/$',
        views.RequirementList.as_view(),
        name='list'),

    url(r'^data/$',
        views.RequirementListJson.as_view(),
        name='json'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.RequirementDetail.as_view(),
        name='detail'),

    url(r'^(?P<pk>[0-9]+)/edit$',
        views.RequirementEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.RequirementDelete.as_view(),
        name='delete'),

    url(r'^(?P<requirement_pk>[0-9]+)/product/',
        include(product_requirement_patterns,
                namespace='product')),
    url(r'^add/$',
        views.RequirementAdd.as_view(),
        name='add'),

    url(r'^(?P<requirement_pk>[0-9]+)/data/',
        include(data_requirement_patterns,
                namespace='data')),
]

data_data_responsible_patterns = [
    url(r'^add/$',
        views.DataDataResponsibleAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataDataResponsibleEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        views.DataDataResponsibleDelete.as_view(),
        name='delete'),
]


data_patterns = [
    url(r'^list/$',
        views.DataList.as_view(),
        name='list'),

    url(r'^data/$',
        views.DataListJson.as_view(),
        name='json'),

    url(r'^add/$',
        views.DataAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataDetail.as_view(),
        name='detail'),

    url(r'^(?P<pk>[0-9]+)/edit$',
        views.DataEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.DataDelete.as_view(),
        name='delete'),

    url(r'^(?P<group_pk>[0-9]+)/responsible/',
        include(data_data_responsible_patterns,
                namespace='responsible')),

    url(r'^(?P<data_pk>[0-9]+)/requirement/',
        include(data_requirement_patterns,
                namespace='requirement')),
]

responsible_patterns = [
    url(r'^list/$',
        views.DataResponsibleList.as_view(),
        name='list'),

    url(r'^data/$',
        views.DataResponsibleListJson.as_view(),
        name='json'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataResponsibleDetail.as_view(),
        name='detail'),

    url(r'^add-network/$',
        views.DataResponsibleAddNetwork.as_view(),
        name='add_network'),

    url(r'^(?P<pk>[0-9]+)/edit-network/$',
        views.DataResponsibleEditNetwork.as_view(),
        name='edit_network'),

    url(r'^(?P<pk>[0-9]+)/delete-network/$',
        views.DataResponsibleDeleteNetwork.as_view(),
        name='delete_network'),

    url(r'^add/$',
        views.DataResponsibleAddNonNetwork.as_view(),
        name='add_non_network'),

    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.DataResponsibleEditNonNetwork.as_view(),
        name='edit_non_network'),

    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.DataResponsibleDeleteNonNetwork.as_view(),
        name='delete_non_network'),

    url(r'^(?P<responsible_pk>[0-9]+)/group/',
        include(data_data_responsible_patterns,
                namespace='group')),
]

auth_patterns = [
    url(r'^login/',
        views.LoginView.as_view(),
        name='login'),
    url(r'^logout/',
        views.LogoutView.as_view(),
        name='logout'),
]

urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(),
        name='home'),

    url(r'^product/',
        include(product_patterns,
                namespace='product')),

    url(r'^requirement/',
        include(requirement_patterns,
                namespace='requirement')),

    url(r'^data/',
        include(data_patterns,
                namespace='data')),

    url(r'^responsible/',
        include(responsible_patterns,
                namespace='responsible')),
    url(r'',
        include(auth_patterns,
                namespace='auth')),

    url(r'picklists$',
        views.PicklistsManager.as_view(),
        name='picklists'),

    url(r'help$',
        views.HelpPage.as_view(),
        name='help')
]