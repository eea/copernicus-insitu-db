from insitu import models as insitu_models
from picklists import models as picklist_models
from factory.django import DjangoModelFactory
from factory import SubFactory


class ProductGroupFactory(DjangoModelFactory):
    name = 'Test product group'
    sort_order = 0

    class Meta:
        model = picklist_models.ProductGroup


class ProductStatusFactory(DjangoModelFactory):
    name = 'Test product status'
    sort_order = 0

    class Meta:
        model = picklist_models.ProductStatus


class CoverageFactory(DjangoModelFactory):
    name = 'Test coverage'
    sort_order = 0

    class Meta:
        model = picklist_models.Coverage


class ServiceFactory(DjangoModelFactory):
    name = 'Test service'

    class Meta:
        model = insitu_models.CopernicusService


class EntrustedEntityFactory(DjangoModelFactory):
    name = 'Test entity'

    class Meta:
        model = insitu_models.EntrustedEntity


class ComponentFactory(DjangoModelFactory):
    name = 'Test component'
    service = SubFactory(ServiceFactory)
    entrusted_entity = SubFactory(EntrustedEntityFactory)

    class Meta:
        model = insitu_models.Component


class ProductFactory(DjangoModelFactory):
    name = 'Test product'
    acronym = 'TST'
    group = SubFactory(ProductGroupFactory)
    component = SubFactory(ComponentFactory)
    status = SubFactory(ProductStatusFactory)
    coverage = SubFactory(CoverageFactory)

    class Meta:
        model = insitu_models.Product
