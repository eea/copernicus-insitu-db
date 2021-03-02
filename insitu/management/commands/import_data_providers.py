from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook
import re
import sys
import csv

from insitu import models as insitu_models
from picklists import models as pickmodels

MODEL_FIELDS = [
    "name",
    "provider_type",
    "description",
    "countries",
    "networks",
    "acronym",
    "website",
    "address",
    "phone",
    "email",
    "contact_person",
]

DATA_PROVIDER_FIELDS = ["name", "description", "countries", "networks"]

DATA_PROVIDER_DETAILS_FIELDS = [
    "provider_type",
    "website",
    "address",
    "phone",
    "email",
    "contact_person",
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("filename", nargs="+", type=str)

    def handle(self, *args, **options):
        filename = options["filename"][0]
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user = insitu_models.User.objects.get(username=row['owner'])
                country = pickmodels.Country.objects.get(code=row['country'])
                if not country:
                    print("Country {} not found".format(row['code']))
                    continue
                provider_type = pickmodels.ProviderType.objects.filter(name=row['type']).first()
                if not provider_type:
                    print("Provider type {} not found".format(row['type']))
                    continue
                data_provider = insitu_models.DataProvider.objects.filter(name=row['name']).first()
                if data_provider:
                    print("Updating data provider {}".format(row['name']))
                    data_provider.edmo = row['edmo']
                    data_provider.countries.add(country)
                    if data_provider.is_network == False:
                        data_provider.details.provider_type = provider_type
                    data_provider.save()
                    continue

                if row['is_network'].lower() == 'true':
                    data_provider = insitu_models.DataProvider.objects.create(
                        is_network=True,
                        name=row['name'],
                        edmo=row['edmo'],
                        created_by=user,
                    )
                    data_provider.countries.add(country)
                    data_provider.save()
                else:
                    data_provider = insitu_models.DataProvider.objects.create(
                        name=row['name'],
                        edmo=row['edmo'],
                        created_by=user,
                    )
                    data_provider.countries.add(country)
                    details = insitu_models.DataProviderDetails(data_provider=data_provider)
                    data_provider.details.provider_type = provider_type
                    data_provider.save()
