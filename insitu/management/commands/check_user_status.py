from django.core.management.base import BaseCommand
from insitu.models import Data, DataProvider, Requirement, User


class Command(BaseCommand):
    help = "Use to transfer all records from one user to another."

    def add_arguments(self, parser):
        parser.add_argument("old_username", type=str)
        parser.add_argument("new_username", type=str)

    def handle(self, *args, **options):
        print(
            f"Transfering data from {options['old_username']} to {options['new_username']}"
        )
        old_user = User.objects.get(username=options["old_username"])
        new_user = User.objects.get(username=options["new_username"])

        requirements_len_old = Requirement.objects.filter(created_by=old_user).count()
        print(f"{old_user} Requirements: {requirements_len_old}")
        requirements_len_new = Requirement.objects.filter(created_by=new_user).count()
        print(f"{new_user} Requirements: {requirements_len_new}")

        data_len_old = Data.objects.filter(created_by=old_user).count()
        print(f"{old_user} Data: {data_len_old}")
        data_len_new = Data.objects.filter(created_by=new_user).count()
        print(f"{new_user} Data: {data_len_new}")

        provider_len_old = DataProvider.objects.filter(created_by=old_user).count()
        print(f"{old_user} Data provider: {provider_len_old}")
        provider_len_new = DataProvider.objects.filter(created_by=new_user).count()
        print(f"{new_user} Data provider: {provider_len_new}")
