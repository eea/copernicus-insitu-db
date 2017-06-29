from picklists import models


def create_product_group(name):
    return models.ProductGroup.objects.get_or_create(name=name)
