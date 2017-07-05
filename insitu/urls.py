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

    url(r'^(?P<product_pk>[0-9]+)/requirement/',
        include(product_requirement_patterns,
                namespace='requirement')),
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

    url(r'^(?P<requirement_pk>[0-9]+)/product/',
        include(product_requirement_patterns,
                namespace='product')),
    url(r'^add/$',
        views.RequirementAdd.as_view(),
        name='add'),
]

data_group_patterns = [
    url(r'^list/$',
        views.DataGroupList.as_view(),
        name='list'),

    url(r'^data/$',
        views.DataGroupListJson.as_view(),
        name='json'),

    url(r'^add/$',
        views.DataGroupAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.DataGroupDetail.as_view(),
        name='detail'),

    url(r'^(?P<pk>[0-9]+)/edit$',
        views.DataGroupEdit.as_view(),
        name='edit'),
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

    url(r'^add/$',
        views.DataResponsibleAddNonNetwork.as_view(),
        name='add_non_network'),

    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.DataResponsibleEditNonNetwork.as_view(),
        name='edit_non_network'),
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

    url(r'^data-group/',
        include(data_group_patterns,
                namespace='data_group')),

    url(r'^responsible/',
        include(responsible_patterns,
                namespace='responsible')),
]
