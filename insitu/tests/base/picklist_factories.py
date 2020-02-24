from factory import Sequence
from picklists import models
from factory.django import DjangoModelFactory


class CountryFactory(DjangoModelFactory):
    code = Sequence(lambda n: "%s" % n)
    name = 'Romania'

    class Meta:
        model = models.Country


class InspireThemeFactory(DjangoModelFactory):
    name = 'Test Theme'
    sort_order = 0
    link = ''

    class Meta:
        model = models.InspireTheme


class EssentialVariableFactory(DjangoModelFactory):
    domain = 'Test domain'
    component = 'Test component'
    parameter = 'Test parameter'
    sort_order = 0
    link = ''

    class Meta:
        model = models.EssentialVariable


class ProductStatusFactory(DjangoModelFactory):
    name = 'Test product status'
    sort_order = 0
    link = ''

    class Meta:
        model = models.ProductStatus


class ProductGroupFactory(DjangoModelFactory):
    name = 'Test product group'
    sort_order = 0

    class Meta:
        model = models.ProductGroup


class RequirementGroupFactory(DjangoModelFactory):
    name = 'Test requirement group'
    sort_order = 0

    class Meta:
        model = models.RequirementGroup


class DefinitionLevelFactory(DjangoModelFactory):
    name = 'Test DefinitionLevel'
    sort_order = 0
    link = ''

    class Meta:
        model = models.DefinitionLevel


class RelevanceFactory(DjangoModelFactory):
    name = 'Test Relevance'
    sort_order = 0
    link = ''

    class Meta:
        model = models.Relevance


class CriticalityFactory(DjangoModelFactory):
    name = 'Test Criticality'
    sort_order = 0
    link = ''

    class Meta:
        model = models.Criticality


class BarrierFactory(DjangoModelFactory):
    name = 'Test Barrier'
    sort_order = 0

    class Meta:
        model = models.Barrier


class DisseminationFactory(DjangoModelFactory):
    name = 'Test Dissemination'
    sort_order = 0
    link = ''

    class Meta:
        model = models.Dissemination


class AreaFactory(DjangoModelFactory):
    name = 'Test area'
    sort_order = 0
    link = ''

    class Meta:
        model = models.Area


class QualityControlProcedureFactory(DjangoModelFactory):
    name = 'Test Quality'
    sort_order = 0
    link = ''

    class Meta:
        model = models.QualityControlProcedure


class ComplianceLevelFactory(DjangoModelFactory):
    name = 'Test ComplianceLevel'
    sort_order = 0
    link = ''

    class Meta:
        model = models.ComplianceLevel


class UpdateFrequencyFactory(DjangoModelFactory):
    name = 'Test UpdateFrequency'
    sort_order = 0
    link = ''

    class Meta:
        model = models.UpdateFrequency


class TimelinessFactory(DjangoModelFactory):
    name = 'Test Timeliness'
    sort_order = 0
    link = ''

    class Meta:
        model = models.Timeliness


class DataPolicyFactory(DjangoModelFactory):
    name = 'Test Data Policy'
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataPolicy


class DataTypeFactory(DjangoModelFactory):
    name = 'Test DataType'
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataType


class DataFormatFactory(DjangoModelFactory):
    name = 'Test DataFormat'
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataFormat


class ProviderTypeFactory(DjangoModelFactory):
    name = 'Test DataProvider'
    sort_order = 0
    link = ''

    class Meta:
        model = models.ProviderType
