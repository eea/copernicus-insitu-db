from django.core.management.base import BaseCommand
from insitu.models import Data, DataProvider, Requirement, User


class Command(BaseCommand):
    help = "Use in case the relation state gets out of sync from the requirement state."

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
        requirements = Requirement.objects.filter(
            created_by__username=options["old_username"]
        )
        self.transfer_ownership_on_objects(requirements, **options)
        data_objects = Data.objects.filter(created_by__username=options["old_username"])
        self.transfer_ownership_on_objects(data_objects, **options)
        dataproviders = DataProvider.objects.filter(
            created_by__username=options["old_username"]
        )
        self.transfer_ownership_on_objects(dataproviders, **options)
