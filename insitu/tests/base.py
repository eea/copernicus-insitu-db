from insitu import models as insitu_models
from picklists import models as picklist_models


def create_product_group():
    return picklist_models.ProductGroup.objects.create(
        name='Test product group',
        sort_order=0)


def create_status():
    return picklist_models.ProductStatus.objects.create(
        name='Test product status',
        sort_order=0)


def create_coverage():
    return picklist_models.Coverage.objects.create(
        name='Test coverage',
        sort_order=0)


def create_service():
    return insitu_models.CopernicusService.objects.create(
        name='Test service')


def create_entity():
    return insitu_models.EntrustedEntity.objects.create(
        name='Test entity')


def create_component():
    return insitu_models.Component.objects.create(
        name='Test component',
        service=create_service(),
        entrusted_entity=create_entity())
