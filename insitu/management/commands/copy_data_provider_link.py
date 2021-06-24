from django.core.management.base import BaseCommand
from insitu.models import Data, DataProviderRelation, User


class Command(BaseCommand):
    help = "Use to duplicate the provider relations from one data to another."

    def add_arguments(self, parser):
        parser.add_argument("old_data", type=int)
        parser.add_argument("new_data", type=int)
        parser.add_argument("user", type=str)

    def handle(self, *args, **options):
        user = User.objects.get(username=options["user"])
        old_data = Data.objects.get(id=options["old_data"])
        new_data = Data.objects.get(id=options["new_data"])
        links = DataProviderRelation.objects.filter(data=old_data, _deleted=False)
        for link in links:
            data_provider = DataProviderRelation.objects.filter(
                data=new_data, provider=link.provider
            )
            if not data_provider:
                DataProviderRelation.objects.create(
                    data=new_data,
                    provider=link.provider,
                    role=link.role,
                    created_by=user,
                )
