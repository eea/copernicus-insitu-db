from django.conf.urls import url

from insitu import views

urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(),
        name='home'),

    url(r'^product/list/$',
        views.ProductList.as_view(),
        name='product_list'),

    url(r'^product/data/$',
        views.ProductListJson.as_view(),
        name='products_json'),

    url(r'^product/add/$',
        views.ProductAdd.as_view(),
        name='product_add'),

    url(r'^product/(?P<pk>[0-9]+)/$',
        views.ProductDetail.as_view(),
        name='product_detail'),

    url(r'^product/(?P<pk>[0-9]+)/edit/$',
        views.ProductEdit.as_view(),
        name='product_edit'),
]
