from django.core.management.base import BaseCommand
from insitu.models import  Data, DataProvider, Requirement


class Command(BaseCommand):
    help = 'Use in case the data provider relation state gets out of sync from the data state.'

    def handle(self, *args, **options):
        data_list = Data.objects.all()
        faulty_data_providers = []
        for data in data_list:
            faulty_data_providers.extend(
                [rel for rel in data.dataproviderrelation_set.all() if rel.state != data.state]
            )
        
        for rel in faulty_data_providers:
            print("Faulty relation: Data:{} - Data Provider:{} , state:{} , data state: {}".format(
               rel.data.id,
               rel.provider.id,
               rel.state,
               rel.data.state
            ))
            rel.state = rel.data.state
            rel.save()
            print("Relation reseted")

