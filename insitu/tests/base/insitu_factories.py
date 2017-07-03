from factory import SubFactory, RelatedFactory, post_generation
from factory.django import DjangoModelFactory

from insitu import models
from insitu.tests.base import picklist_factories as factories


class MetricFactory(DjangoModelFactory):
    threshold = 'test threshold'
    breakthrough = 'test breakthrough'
    goal = 'test goal'

    class Meta:
        model = models.Metric


class CopernicusServiceFactory(DjangoModelFactory):
    name = 'Test service'

    class Meta:
        model = models.CopernicusService


class EntrustedEntityFactory(DjangoModelFactory):
    name = 'Test entity'

    class Meta:
        model = models.EntrustedEntity


class ComponentFactory(DjangoModelFactory):
    name = 'Test component'
    service = SubFactory(CopernicusServiceFactory)
    entrusted_entity = SubFactory(EntrustedEntityFactory)

    class Meta:
        model = models.Component


class RequirementFactory(DjangoModelFactory):
    name = 'Test requirement'
    dissemination = SubFactory(factories.DisseminationFactory)
    quality = SubFactory(factories.QualityFactory)
    uncertainty = SubFactory(MetricFactory)
    frequency = SubFactory(MetricFactory)
    timeliness = SubFactory(MetricFactory)
    horizontal_resolution = SubFactory(MetricFactory)
    vertical_resolution = SubFactory(MetricFactory)

    class Meta:
        model = models.Requirement


class ProductFactory(DjangoModelFactory):
    name = 'Test product'
    acronym = 'TST'
    group = SubFactory(factories.ProductGroupFactory)
    component = SubFactory(ComponentFactory)
    status = SubFactory(factories.ProductStatusFactory)
    coverage = SubFactory(factories.CoverageFactory)

    class Meta:
        model = models.Product


class ProductRequirementFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    requirement = SubFactory(RequirementFactory)
    level_of_definition = SubFactory(factories.DefinitionLevelFactory)
    distance_to_target = SubFactory(factories.TargetDistanceFactory)
    relevance = SubFactory(factories.RelevanceFactory)
    criticality = SubFactory(factories.CriticalityFactory)
    barriers = RelatedFactory(factories.BarrierFactory)

    class Meta:
        model = models.ProductRequirement


class DataResponsibleFactory(DjangoModelFactory):
    name = 'test data responsible'
    countries = RelatedFactory(factories.CountryFactory)

    class Meta:
        model = models.DataResponsible


class DataResponsibleDetailsFactory(DjangoModelFactory):
    acronym = 'TST'
    website = 'test website'
    address = 'test address'
    phone = 'test phone'
    email = 'test email'
    contact_person = 'test contact'
    responsible_type = models.DataResponsibleDetails.TYPE_CHOICES[0][0]
    data_responsible = SubFactory(DataResponsibleFactory)

    class Meta:
        model = models.DataResponsibleDetails


class DataGroupFactory(DjangoModelFactory):
    name = 'test DataGroup'
    frequency = SubFactory(factories.FrequencyFactory)
    coverage = SubFactory(factories.CoverageFactory)
    timeliness = SubFactory(factories.TimelinessFactory)
    policy = SubFactory(factories.PolicyFactory)
    data_type = SubFactory(factories.DataTypeFactory)
    data_format = SubFactory(factories.DataFormatFactory)
    quality = SubFactory(factories.QualityFactory)
    inspire_themes = RelatedFactory(factories.InspireThemeFactory)
    # requirements = SubFactory(RequirementFactory)
    # responsibles = SubFactory(DataResponsibleFactory)

    class Meta:
        model = models.DataGroup


class DataRequirementFactory(DjangoModelFactory):
    data_group = SubFactory(DataGroupFactory)
    requirement = SubFactory(RequirementFactory)
    level_of_compliance = SubFactory(factories.ComplianceLevelFactory)

    class Meta:
        model = models.DataRequirement


class DataResponsibleRelationFactory(DjangoModelFactory):
    data_group = SubFactory(DataGroupFactory)
    responsible = SubFactory(DataResponsibleFactory)
    role = models.DataResponsibleRelation.ROLE_CHOICES[0][0]

    class Meta:
        model = models.DataResponsibleRelation
