# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices, ALL_OPTIONS_LABEL
from insitu.views.base import ESDatatableView
from insitu.views.protected import (
    ProtectedView,
    ProtectedTemplateView, ProtectedDetailView,
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from insitu.views.protected.permissions import (
    IsAuthenticated,
    IsCopernicusServiceResponsible,
)
from picklists import models as pickmodels


class ProductList(ProtectedTemplateView):
    template_name = 'product/list.html'
    permission_classes = (IsAuthenticated, )
    permission_denied_redirect = None

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:login')
        return super().permission_denied(request)

    def get_context_data(self):
        context = super(ProductList, self).get_context_data()
        services = get_choices('name', model_cls=models.CopernicusService)
        groups = get_choices('name', model_cls=pickmodels.ProductGroup)
        statuses = get_choices('name', model_cls=pickmodels.ProductStatus)
        coverages = get_choices('name', model_cls=pickmodels.Coverage)
        components = get_choices('name', model_cls=models.Component)
        entities = get_choices('acronym', model_cls=models.EntrustedEntity)
        context.update({
            'services': services,
            'groups': groups,
            'statuses': statuses,
            'coverages': coverages,
            'components': components,
            'entities': entities,
        })
        return context


class ProductListJson(ESDatatableView):
    columns = ['acronym', 'name', 'group', 'service', 'component', 'entity',
               'status', 'coverage']
    order_columns = columns
    filters = ['service', 'group', 'status', 'coverage', 'component', 'entity']
    document = documents.ProductDoc


class ComponentsFilter(ProtectedView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        service = request.GET.get('service', '')
        entity = request.GET.get('entity', '')

        components = models.Component.objects.all()
        if service and service != ALL_OPTIONS_LABEL:
            components = components.filter(service__name=service)
        if entity and entity != ALL_OPTIONS_LABEL:
            components = components.filter(entrusted_entity__acronym=entity)
        data = {'components': get_choices('name', objects=components)}
        return JsonResponse(data)


class ProductAdd(ProtectedCreateView):
    template_name = 'product/add.html'
    form_class = forms.ProductForm
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('product:list')
        return super().permission_denied(request)

    def get_success_url(self):
        return reverse('product:list')




class ProductEdit(ProtectedUpdateView):
    template_name = 'product/edit.html'
    form_class = forms.ProductForm
    model = models.Product
    context_object_name = 'product'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('product:list')
        return super().permission_denied(request)

    def get_success_url(self):
        product = self.get_object()
        return reverse('product:detail', kwargs={'pk': product.pk})


class ProductDetail(ProtectedDetailView):
    template_name = 'product/detail.html'
    model = models.Product
    context_object_name = 'product'
    permission_classes = (IsAuthenticated, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:login')
        return super().permission_denied(request)


class ProductDelete(ProtectedDeleteView):

    template_name = 'product/delete.html'
    form_class = forms.ProductForm
    model = models.Product
    context_object_name = 'product'
    permission_classes = (IsCopernicusServiceResponsible, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('product:list')
        return super().permission_denied(request)

    def get_success_url(self):
        return reverse('product:list')
