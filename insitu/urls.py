from django.conf.urls import url, include

from insitu import views


product_requirement_patterns = [
    url(r'^add/$',
        views.ProductRequirementAdd.as_view(),
        name='add'),

    url(r'^add-group/$',
        views.ProductGroupRequirementAdd.as_view(),
        name='add_group'),

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

    url(r'^export$',
        views.ExportProductView.as_view(),
        name='export'),

    url(r'import$',
        views.ImportProductsView.as_view(),
        name='import')
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

    url(r'^(?P<pk>[0-9]+)/transition/(?P<source>[a-z]+)-to-(?P<target>[a-z]+)/$',
        views.RequirementTransition.as_view(),
        name='transition'),

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

data_data_provider_patterns = [
    url(r'^add/$',
        views.DataDataProviderAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataDataProviderEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        views.DataDataProviderDelete.as_view(),
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

    url(r'^(?P<group_pk>[0-9]+)/provider/',
        include(data_data_provider_patterns,
                namespace='provider')),
]

provider_patterns = [
    url(r'^list/$',
        views.DataProviderList.as_view(),
        name='list'),

    url(r'^data/$',
        views.DataProviderListJson.as_view(),
        name='json'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataProviderDetail.as_view(),
        name='detail'),

    url(r'^add-network/$',
        views.DataProviderAddNetwork.as_view(),
        name='add_network'),

    url(r'^(?P<pk>[0-9]+)/edit-network/$',
        views.DataProviderEditNetwork.as_view(),
        name='edit_network'),

    url(r'^(?P<pk>[0-9]+)/edit-network-members/$',
        views.DataProviderEditNetworkMembers.as_view(),
        name='edit_network_members'),

    url(r'^(?P<pk>[0-9]+)/delete-network/$',
        views.DataProviderDeleteNetwork.as_view(),
        name='delete_network'),

    url(r'^add/$',
        views.DataProviderAddNonNetwork.as_view(),
        name='add_non_network'),

    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.DataProviderEditNonNetwork.as_view(),
        name='edit_non_network'),

    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.DataProviderDeleteNonNetwork.as_view(),
        name='delete_non_network'),
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

    url(r'^provider/',
        include(provider_patterns,
                namespace='provider')),
    url(r'',
        include(auth_patterns,
                namespace='auth')),

    url(r'manage$',
        views.Manager.as_view(),
        name='manage'),

    url(r'help$',
        views.HelpPage.as_view(),
        name='help'),
    url(r'crashme$',
        views.Crashme.as_view(),
        name='crashme')
]
