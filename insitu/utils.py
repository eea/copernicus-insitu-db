from contextlib import contextmanager
import xlsxwriter
from io import BytesIO
from django.http import HttpResponse

from insitu.models import Data, DataProvider, Product, Requirement

ALL_OPTIONS_LABEL = "All"

PICKLISTS_DESCRIPTION = {
    "Barrier": (
        "High level barriers used to illustrate the main reasons why a given in "
        "situ data requirement cannot be meet for the product in question."
    ),
    "Criticality": (
        "A measure of the relevance of the requirement for the provision of "
        "reliable products."
    ),
    "ComplianceLevel": (
        "A measure of how much the data set  addresses the given requirement."
    ),
    "Area": (
        "The specific boundaries of the geographic or political region for "
        "which in situ data is required."
    ),
    "DataFormat": (
        "The general category of format with whom the in situ data is provided."
    ),
    "DataType": (
        "Provide a classification of in situ data which characterise how the "
        "data contents are represented."
    ),
    "DefinitionLevel": (
        "A requirement, essential for a product or family of products, for in "
        "situ measurement of a critical physical, chemical or biological variable."
    ),
    "Dissemination": "The technical means by which the in situ data is accessed.",
    "EssentialVariable": (
        "A requirement, essential for a product or family of products, for in "
        "situ measurement of a critical physical, chemical or biological variable."
    ),
    "InspireTheme": (
        "The INSPIRE theme register contains all spatial data themes, as "
        "defined in the Annexes of theINSPIRE Directive ( Directive 2007/2/EC )."
    ),
    "DataPolicy": (
        "The policy dictated terms associated with access to required data and "
        "any associated costs."
    ),
    "ProviderType": (
        "The following definitions mainly refer to the Primary Role of the "
        "provider and the funding nature. It is recommended to only use "
        "Commercial, Institutional and Research categories."
    ),
    "ProductGroup": (
        "The product group attribute is used to assemble a group (or product "
        "family) of individual products under the same heading.This attribute "
        "is used in addition to other relevant ways of classifying a given "
        "product including coverage and status."
    ),
    "Status": (
        "This attribute is used to classify a given product according to its "
        "matureness or operational status."
    ),
    "RequirementGroup": (
        "A classification of  requirements oriented to group them with respect "
        "to the prevalent information contents of the underlying data sets."
    ),
    "ResponsibleGroup": (
        "A classification of  requirements oriented to group them with respect "
        "to the prevalent information contents of the underlying data sets."
    ),
    "ResponsibleType": (
        "Define the  main categories  of the  party responsible for the "
        "provision of the  in situ data."
    ),
    "Relevance": (
        "Categorisation of the way in which the data is utilised and the "
        "associated level of criticality."
    ),
    "QualityControlProcedure": (
        "Source of in situ data measurement and associated level of data assurance."
    ),
    "Timeliness": "Maximum delay to data reception to satisfy requirements.",
    "UpdateFrequency": "Maximum delay to data currency to satisfy requirements.",
}


def get_choices(field, model_cls=None, objects=None):
    model_values = []
    if model_cls:
        model_values = list(model_cls.objects.values_list(field, flat=True))
    elif objects:
        model_values = list(objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values

def get_name(obj_id, obj_type):
    name = ''
    if obj_id:
        if obj_type == 'requirement':
            name = Requirement.objects.really_all().filter(id=obj_id).first().name
        elif obj_type == 'data':
            name = Data.objects.really_all().filter(id=obj_id).first().name
        elif obj_type == 'product':
            name = Product.objects.really_all().filter(id=obj_id).first().name
        elif obj_type == 'data provider':
            name = DataProvider.objects.really_all().filter(id=obj_id).first().name
    return name

def export_logs_excel(queryset):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"remove_timezone": True})
    date_format = workbook.add_format({"num_format": "d mmm yyyy hh:mm AM/PM"})
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "Date")
    worksheet.write(0, 1, "User")
    worksheet.write(0, 2, "Action")
    worksheet.write(0, 3, "Target type")
    worksheet.write(0, 4, "Target ID")
    worksheet.write(0, 5, "Target Name")
    worksheet.write(0, 6, "Extra")

    row = 1
    for obj in queryset:
        worksheet.write(row, 0, obj.logged_date, date_format)
        worksheet.write(row, 1, obj.user)
        worksheet.write(row, 2, obj.action)
        worksheet.write(row, 3, obj.target_type)
        worksheet.write(row, 4, obj.id_target)
        worksheet.write(row, 5, get_name(obj.id_target, obj.target_type))
        worksheet.write(row, 6, obj.extra)
        row += 1
    workbook.close()

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment;filename="user_actions_logs.xlsx"'
    response.write(output.getvalue())
    return response


@contextmanager
def soft_deleted(obj):
    obj._deleted = True
    obj.save()
    yield obj
    obj._deleted = False
    obj.save()
