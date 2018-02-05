from picklists import models
from factory import Sequence
from factory.django import DjangoModelFactory


class CountryFactory(DjangoModelFactory):
    code = 'RO'
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
    name = Sequence(lambda n: "Test product status %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.ProductStatus


class ProductGroupFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test product group %d" % n)
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
    name = Sequence(lambda n: "Test Dissemination %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.Dissemination


class AreaFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test area %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.Area


class QualityControlProcedureFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test Quality %d" % n)
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
    name = Sequence(lambda n: "Test UpdateFrequency %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.UpdateFrequency


class TimelinessFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test Timeliness %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.Timeliness


class DataPolicyFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test Data Policy %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataPolicy


class DataTypeFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test DataType %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataType


class DataFormatFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test DataFormat %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.DataFormat


class ProviderTypeFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Test DataProvider %d" % n)
    sort_order = 0
    link = ''

    class Meta:
        model = models.ProviderType
