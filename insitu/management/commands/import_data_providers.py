from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook
import re
import sys


from insitu import models as insitu_models
from picklists import models as pickmodels

MODEL_FIELDS = ['name', 'provider_type', 'description', 'countries', 'networks',
                'acronym', 'website', 'address', 'phone', 'email', 'contact_person']

DATA_PROVIDER_FIELDS = ['name', 'description', 'countries', 'networks']

DATA_PROVIDER_DETAILS_FIELDS = ['provider_type', 'website', 'address', 'phone',
                                'email', 'contact_person']

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        wb = load_workbook(filename=filename)
        ws = wb.get_sheet_by_name('Ark1')
        with transaction.atomic():
            fields = MODEL_FIELDS
            for row in ws.iter_rows(min_row=5):
                has_network = False
                data_provider_details = {}
                data_provider = {}
                networks = []
                countries = []
                for i in range(0, len(fields)-1):
                    field = fields[i]
                    value = row[i].value if row[i].value is not None else ''
                    if field in DATA_PROVIDER_DETAILS_FIELDS:
                        if field == 'provider_type':
                            provider_type_model = pickmodels.ProviderType.objects.filter(
                                name=value).first()
                            data_provider_details[field] = provider_type_model
                        else:
                            data_provider_details[field] = value
                    elif field in DATA_PROVIDER_FIELDS:
                        if field == 'countries':
                            country = pickmodels.Country.objects.filter(
                                name=value).first()
                            countries.append(country)
                        elif field == 'networks':
                            networks_name = re.split(', ', value)
                            if networks_name != ['']:
                                has_network = True
                                for network_name in networks_name:
                                    network = insitu_models.DataProvider.objects.filter(name__iexact=network_name).first()
                                    networks.append(network)
                        else:
                            data_provider[field] = value
                if has_network:
                    user_id = get_user_model().objects.get(email='erik.buch@eurogoos.eu').id
                    data_provider_obj = insitu_models.DataProvider.objects.create(created_by_id=user_id, **data_provider)
                    data_provider_obj.countries = countries
                    data_provider_obj.networks = networks
                    insitu_models.DataProviderDetails.objects.create(data_provider_id=data_provider_obj.id, created_by_id=user_id, **data_provider_details)
                else:
                    print("\nWarning! Data provider", data_provider['name'],
                          "hasn't been inserted because it doens't have any networks related")
                sys.stdout.write('.')
                sys.stdout.flush()
        print()
