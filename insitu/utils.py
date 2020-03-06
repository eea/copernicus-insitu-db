ALL_OPTIONS_LABEL = 'All'

PICKLISTS_DESCRIPTION = {
    'Barrier': 'High level barriers used to illustrate the main reasons why a given in situ data requirement cannot be meet for the product in question.',
    'Criticality': 'A measure of the relevance of the requirement for the provision of reliable products.',
    'ComplianceLevel': 'A measure of how much the data set  addresses the given requirement.',
    'Area': 'The specific boundaries of the geographic or political region for which in situ data is required.',
    'DataFormat': 'The general category of format with whom the in situ data is provided.',
    'DataType': 'Provide a classification of in situ data which characterise how the data contents are represented.',
    'DefinitionLevel': 'A requirement, essential for a product or family of products, for in situ measurement of a critical physical, chemical or biological variable.',
    'Dissemination': 'The technical means by which the in situ data is accessed.',
    'EssentialVariable': 'A requirement, essential for a product or family of products, for in situ measurement of a critical physical, chemical or biological variable.',
    'InspireTheme': 'The INSPIRE theme register contains all spatial data themes, as defined in the Annexes of theINSPIRE Directive ( Directive 2007/2/EC ).',
    'DataPolicy': 'The policy dictated terms associated with access to required data and any associated costs.',
    'ProductGroup': 'The product group attribute is used to assemble a group (or product family) of individual products under the same heading.This attribute is used in addition to other relevant ways of classifying a given product including coverage and status.',
    'Status': 'This attribute is used to classify a given product according to its matureness or operational status.',
    'RequirementGroup': 'A classification of  requirements oriented to group them with respect to the prevalent information contents of the underlying data sets.',

    'ResponsibleGroup': 'A classification of  requirements oriented to group them with respect to the prevalent information contents of the underlying data sets.',
    'ResponsibleType': 'Define the  main categories  of the  party responsible for the  provision of the  in situ data.',
    'Relevance': 'Categorisation of the way in which the data is utilised and the associated level of criticality.',
    'QualityControlProcedure': 'Source of in situ data measurement and associated level of data assurance.',
    'Timeliness': 'Maximum delay to data reception to satisfy requirements.',
    'UpdateFrequency': 'Maximum delay to data currency to satisfy requirements.',

}


def get_choices(field, model_cls=None, objects=None):
    model_values = []
    if model_cls:
        model_values = list(model_cls.objects.values_list(field, flat=True))
    elif objects:
        model_values = list(objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values
