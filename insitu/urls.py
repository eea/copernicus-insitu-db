from django.conf.urls import url

from insitu import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^product/list/$', views.ProductList.as_view(), name='product_list'),
    url(r'^product/data/$', views.ProductListJson.as_view(),
        name='products_json'),
    url(r'^product/add/$', views.ProductAdd.as_view(), name='product_add'),
]
