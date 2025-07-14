import csv

from django.core.management.base import BaseCommand

from insitu import models as insitu_models


class Command(BaseCommand):
    """Command that will receive a CSV file with a list of data providers IDs and for
    each data provider it will set the native name to the data provider's name.
    This script is used to update the native names for English-speaking countries.

    Run as follows:
    python manage.py set_data_providers_native_names --filename <path_to_csv_file> --dry-run True
    or
    python manage.py set_data_providers_native_names --filename <path_to_csv_file>
    """

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str)
        parser.add_argument(
            "--dry-run",
            type=bool,
            help="If True, the command will not save changes to the database.",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        with open(filename, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            data_providers = []
            for row in reader:
                id = row["id"]
                try:
                    data_provider = insitu_models.DataProvider.objects.get(id=id)
                except insitu_models.DataProvider.DoesNotExist:
                    print("Data provider with ID {} not found".format(id))
                    continue
                data_providers.append(data_provider)
                data_provider.native_name = data_provider.name

            if options["dry_run"]:
                print("Dry run: no changes will be saved to the database.")
            else:
                insitu_models.DataProvider.objects.bulk_update(
                    data_providers, ["native_name"]
                )
                print(
                    "Updated {} data providers with native names.".format(
                        len(data_providers)
                    )
                )
