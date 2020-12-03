from django.core.management.base import BaseCommand
from insitu.models import Data


class Command(BaseCommand):
    help = (
        "Use in case the data provider relation state gets out of sync from "
        "the data state."
    )

    def handle(self, *args, **options):
        data_list = Data.objects.all()
        faulty_data_providers = []
        for data in data_list:
            faulty_data_providers.extend(
                [
                    rel
                    for rel in data.dataproviderrelation_set.all()
                    if rel.state != data.state
                ]
            )

        for rel in faulty_data_providers:
            print(
                f"Faulty relation: Data:{rel.data.id}"
                f" - Data Provider:{rel.provider.id}"
                f" , state:{rel.state}"
                f" , data state: {rel.data.state}"
            )
            rel.state = rel.data.state
            rel.save()
            print("Relation reseted")
