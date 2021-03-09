from django.core.management.base import BaseCommand

from insitu import models as insitu_models
from picklists import models as pickmodels


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_providers = insitu_models.DataProvider.objects.filter(is_network=True)
        provider_type = pickmodels.ProviderType.objects.filter(name="N/A").first()
        for data_provider in data_providers:
            if not data_provider.details.first():
                insitu_models.DataProviderDetails.objects.create(
                    data_provider=data_provider,
                    provider_type=provider_type,
                    created_by=data_provider.created_by,
                )
                data_provider.save()
