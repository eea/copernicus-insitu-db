# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.http import HttpResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from insitu.views import protected
from picklists import models

PICKLISTS = [
    models.Barrier, models.ComplianceLevel, models.Coverage, models.Criticality,
    models.Country, models.DataFormat, models.DataType, models.DefinitionLevel,
    models.Dissemination, models.EssentialClimateVariable, models.Frequency,
    models.InspireTheme, models.ProductGroup, models.ProductStatus,
    models.Relevance, models.Quality, models.Timeliness, models.Policy
]


class ExportPicklistsView(protected.ProtectedView):
    permission_classes = (protected.IsCopernicusServiceResponsible, )

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="picklists.xlsx"'
        wb = Workbook()
        wb.remove(wb.active)

        for model in PICKLISTS:
            # Create sheet
            ws = wb.create_sheet(model._meta.model_name)

            # Header
            current_row = 1
            columns = [field.name for field in model._meta.get_fields()
                       if not isinstance(field, ForeignObjectRel)]
            for col in columns:
                cell = ws.cell(row=current_row,
                               column=columns.index(col) + 1,
                               value=col)
                cell.font = Font(bold=True)

            # Data
            data = model.objects.all()
            for entry in data:
                current_row += 1
                for col in columns:
                    ws.cell(row=current_row,
                            column=columns.index(col) + 1,
                            value=getattr(entry, col))
            if 'id' == columns[0]:
                ws.column_dimensions.group(start='A',
                                           end='A',
                                           hidden=True)
            ws.freeze_panes = 'A2'
        wb.save(response)
        return response


class ImportPicklistsView(protected.ProtectedView):
    permission_classes = (protected.IsCopernicusServiceResponsible, )

    def post(self, request, *args, **kwargs):
        if not 'workbook' in request.FILES:
            return HttpResponse(status=400)
        workbook_file = request.FILES['workbook']
        try:
            wb = load_workbook(workbook_file)
            models = {model._meta.model_name: model for model in PICKLISTS}

            with transaction.atomic():
                for sheet_name in wb.get_sheet_names():
                    ws = wb.get_sheet_by_name(sheet_name)
                    model = models.get(sheet_name)
                    fields = [col[0].value for col in ws.iter_cols(min_row=1, max_row=1)]

                    for row in ws.iter_rows(min_row=2):
                        data = {}
                        pk = row[0].value
                        for i in range(1, len(row)):
                            data[fields[i]] = (
                                row[i].value if row[i].value is not None else ''
                            )
                        if pk is not None:
                            model.objects.filter(pk=pk).update(**data)
                        else:
                            model.objects.create(**data)
        except:
            return HttpResponse(status=400)
        return HttpResponse(status=200)
