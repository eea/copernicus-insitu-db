from django.core.management.base import BaseCommand
from insitu.models import Data, DataProvider, Requirement, User


class Command(BaseCommand):
    help = "Use to transfer all records from one user to another."

    def add_arguments(self, parser):
        parser.add_argument("old_username", type=str)
        parser.add_argument("new_username", type=str)

    def transfer_ownership_on_objects(self, objects, **options):
        new_user = User.objects.get(username=options["new_username"])
        for data_object in objects:
            data_object.created_by = new_user
            data_object.save()
            objects = data_object.get_related_objects()
            for related_object in objects:
                related_object.created_by = new_user
                related_object.save()

    def handle(self, *args, **options):
        print(
            f"Transfering data from {options['old_username']} to "
            f"{options['new_username']}"
        )
        old_user = User.objects.get(username=options["old_username"])
        objects = Requirement.objects.filter(created_by=old_user)
        print(f"Transfering requirements...{objects}")
        self.transfer_ownership_on_objects(objects, **options)
        objects = Data.objects.filter(created_by=old_user)
        print(f"Transfering data...{objects}")
        self.transfer_ownership_on_objects(objects, **options)
        objects = DataProvider.objects.filter(created_by=old_user)
        print(f"Transfering providers...{objects}")
        self.transfer_ownership_on_objects(objects, **options)
