from django.core.management.base import BaseCommand

from insitu import models as insitu_models
from fuzzywuzzy import fuzz


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_providers = insitu_models.DataProvider.objects.all()
        data_providers2 = insitu_models.DataProvider.objects.all()
        for data_provider in data_providers:
            for data_provider2 in data_providers2.exclude(id=data_provider.id):
                Ratio = fuzz.ratio(data_provider.name, data_provider2.name)
                if Ratio > 85:
                    print(
                        "Ration between {} - {} is {}".format(
                            data_provider.id, data_provider2.id, Ratio
                        )
                    )
