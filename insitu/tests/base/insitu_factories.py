from django.contrib.auth.models import User

from factory import SubFactory, RelatedFactory, post_generation
from factory.django import DjangoModelFactory

from insitu import models
from insitu.tests.base import picklist_factories as factories


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User


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
    note = 'Test note'
    dissemination = SubFactory(factories.DisseminationFactory)
    quality_control_procedure = SubFactory(
        factories.QualityControlProcedureFactory
    )
    group = SubFactory(factories.RequirementGroupFactory)
    uncertainty = SubFactory(MetricFactory)
    update_frequency = SubFactory(MetricFactory)
    timeliness = SubFactory(MetricFactory)
    horizontal_resolution = SubFactory(MetricFactory)
    vertical_resolution = SubFactory(MetricFactory)

    @staticmethod
    def create_metrics(creator):
        data = {
            'uncertainty': MetricFactory(created_by=creator),
            'update_frequency': MetricFactory(created_by=creator),
            'timeliness': MetricFactory(created_by=creator),
            'horizontal_resolution': MetricFactory(created_by=creator),
            'vertical_resolution': MetricFactory(created_by=creator)
        }
        return data

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
    relevance = SubFactory(factories.RelevanceFactory)
    criticality = SubFactory(factories.CriticalityFactory)
    barriers = RelatedFactory(factories.BarrierFactory)

    class Meta:
        model = models.ProductRequirement


class DataProviderFactory(DjangoModelFactory):
    name = 'test data provider'
    countries = RelatedFactory(factories.CountryFactory)

    class Meta:
        model = models.DataProvider


class DataProviderDetailsFactory(DjangoModelFactory):
    acronym = 'TST'
    website = 'test website'
    address = 'test address'
    phone = 'test phone'
    email = 'test email'
    contact_person = 'test contact'
    provider_type = SubFactory(factories.ProviderTypeFactory)
    data_provider = SubFactory(DataProviderFactory)

    class Meta:
        model = models.DataProviderDetails


class DataFactory(DjangoModelFactory):
    name = 'test Data'
    update_frequency = SubFactory(factories.UpdateFrequencyFactory)
    coverage = SubFactory(factories.CoverageFactory)
    timeliness = SubFactory(factories.TimelinessFactory)
    policy = SubFactory(factories.PolicyFactory)
    data_type = SubFactory(factories.DataTypeFactory)
    data_format = SubFactory(factories.DataFormatFactory)
    quality_control_procedure = SubFactory(
        factories.QualityControlProcedureFactory
    )
    inspire_themes = RelatedFactory(factories.InspireThemeFactory)
    dissemination = SubFactory(factories.DisseminationFactory)
    # requirements = SubFactory(RequirementFactory)
    # providers = SubFactory(DataProviderFactory)

    class Meta:
        model = models.Data


class DataRequirementFactory(DjangoModelFactory):
    data = SubFactory(DataFactory)
    requirement = SubFactory(RequirementFactory)
    level_of_compliance = SubFactory(factories.ComplianceLevelFactory)

    class Meta:
        model = models.DataRequirement


class DataProviderRelationFactory(DjangoModelFactory):
    data = SubFactory(DataFactory)
    provider = SubFactory(DataProviderFactory)
    role = models.DataProviderRelation.ROLE_CHOICES[0][0]

    class Meta:
        model = models.DataProviderRelation


class CopernicususProviderFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    service = SubFactory(CopernicusServiceFactory)

    class Meta:
        model = models.CopernicusProvider


class CountryProvider(DjangoModelFactory):
    user = SubFactory(UserFactory)
    country = SubFactory(factories.CountryFactory)

    class Meta:
        model = models.CountryProvider


class DataProviderUserManager(DjangoModelFactory):
    user = SubFactory(UserFactory)
    provider = SubFactory(DataProviderFactory)

    class Meta:
        model = models.DataProviderUser
