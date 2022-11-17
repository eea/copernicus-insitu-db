from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

# from insitu.models import (
#     Requirement,
#     Data,
#     Product,
#     DataProvider,
#     LoggedAction
# )
from insitu.models import LoggedAction


class Command(BaseCommand):
    help = "Command to fill in 'target_note' for LoggedAction"

    def handle(self, *args, **options):
        # Requirement
        print("\n\nFill target note for REQUIREMENT")
        print("------------------------------")
        req_ct = ContentType.objects.get(model="requirement")
        logged_reqs = LoggedAction.objects.filter(target_type="requirement")

        for logged_req in logged_reqs:
            if logged_req.id_target:
                try:
                    req = req_ct.get_object_for_this_type(pk=logged_req.id_target)
                except ObjectDoesNotExist:
                    print(f"Requirement not found for pk {logged_req.id_target}")
                    continue

                logged_req.target_note = req.note
                logged_req.save()
                print(
                    f"Saved note for LoggedAction {logged_req.pk} requirement {req.pk}"
                )

        # Product
        print("\n\nFill target note for PRODUCT")
        print("------------------------------")
        product_ct = ContentType.objects.get(model="product")
        logged_products = LoggedAction.objects.filter(target_type="product")

        for logged_product in logged_products:
            if logged_product.id_target:
                try:
                    product = product_ct.get_object_for_this_type(
                        pk=logged_product.id_target
                    )
                except ObjectDoesNotExist:
                    print(f"Product not found for pk {logged_product.id_target}")
                    continue

                logged_product.target_note = product.note
                logged_product.save()
                print(
                    f"Saved note for LoggedAction {logged_product.pk} "
                    f"product {product.pk}"
                )

        # Data
        print("\n\nFill target note for DATA")
        print("---------------------------")
        data_ct = ContentType.objects.get(model="data")
        logged_datas = LoggedAction.objects.filter(target_type="data")

        for logged_data in logged_datas:
            if logged_data.id_target:
                try:
                    data = data_ct.get_object_for_this_type(pk=logged_data.id_target)
                except ObjectDoesNotExist:
                    print(f"Data not found for pk {logged_data.id_target}")
                    continue

                logged_data.target_note = data.note
                logged_data.save()
                print(f"Saved note for LoggedAction {logged_data.pk} data {data.pk}")

        # DataProvider
        print("\n\nFill target note for DATA PROVIDER")
        print("----------------------------------")
        datap_ct = ContentType.objects.get(model="dataprovider")
        logged_dataps = LoggedAction.objects.filter(target_type="data provider")

        for logged_datap in logged_dataps:
            if logged_datap.id_target:
                try:
                    datap = datap_ct.get_object_for_this_type(pk=logged_datap.id_target)
                except ObjectDoesNotExist:
                    print(f"Data Provider not found for pk {logged_datap.id_target}")
                    continue

                logged_datap.target_note = datap.description
                logged_datap.save()
                print(
                    f"Saved note for LoggedAction {logged_datap.pk} data "
                    f"provider {datap.pk}"
                )
