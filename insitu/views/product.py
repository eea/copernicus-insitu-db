# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.http.response import JsonResponse, HttpResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

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
    IsSuperuser,
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
    permission_classes = (IsAuthenticated, )


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
    permission_classes = (IsSuperuser, )

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
    permission_classes = (IsSuperuser, )

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
    permission_classes = (IsSuperuser, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('product:list')
        return super().permission_denied(request)

    def get_success_url(self):
        return reverse('product:list')


SKIP_FIELDS = ['_deleted', 'requirements', 'created_at', 'updated_at']


class ExportProductView(ProtectedView):
    permission_classes = (IsSuperuser,)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'
        wb = Workbook()
        wb.remove(wb.active)

        ws = wb.create_sheet('product')
        # Header
        current_row = 1
        columns = [field for field in models.Product._meta.get_fields()
                   if not isinstance(field, ForeignObjectRel) and field.name not in
                   SKIP_FIELDS]
        for col in columns:
            cell = ws.cell(row=current_row,
                           column=columns.index(col) + 1,
                           value=col.name)
            cell.font = Font(bold=True)

        # Data
        data = models.Product.objects.all()
        for entry in data:
            current_row += 1
            for col in columns:
                value = getattr(entry, col.name)
                if col.related_model:
                    value = value.pk
                ws.cell(row=current_row,
                        column=columns.index(col) + 1,
                        value=value)
        ws.freeze_panes = 'A2'
        wb.save(response)
        return response


RELATED_FIELDS = {
    'group': pickmodels.ProductGroup,
    'component': models.Component,
    'status': pickmodels.ProductStatus,
    'coverage': pickmodels.Coverage,
}


class ImportProductsView(ProtectedView):
    permission_classes = (IsSuperuser,)

    def post(self, request, *args, **kwargs):
        if not 'workbook' in request.FILES:
            return HttpResponse(status=400)
        workbook_file = request.FILES['workbook']
        try:
            wb = load_workbook(workbook_file)
            with transaction.atomic():
                ws = wb.get_sheet_by_name('product')
                fields = [
                    col[0].value
                    for col in ws.iter_cols(min_row=1, max_row=1)
                    if col[0].value is not None
                ]
                print(fields)
                for row in ws.iter_rows(min_row=2):
                    data = {}
                    pk = row[0].value
                    for i in range(1, len(fields)):
                        field = fields[i]
                        value = row[i].value if row[i].value is not None else ''
                        if field in RELATED_FIELDS.keys():
                            value = RELATED_FIELDS[field].objects.get(pk=value)
                        data[field] = value
                    if not [val for val in data.values() if val]:
                        continue
                    print(pk, data)
                    models.Product.objects.update_or_create(pk=pk, defaults=data)
        except:
            return HttpResponse(status=400)
        return HttpResponse(status=200)
