from django.core.management.base import BaseCommand
from insitu.models import  Data, DataProvider, Requirement, User


class Command(BaseCommand):
    help = 'Use in case the relation state gets out of sync from the requirement state.'

    def add_arguments(self, parser):
        parser.add_argument('object_type', type=str)
        parser.add_argument('new_username', type=str)
        parser.add_argument('filename', type=str)

    def transfer_ownership_on_objects(self, objects, **options):
        new_user = User.objects.get(username=options['new_username'])
        for data_object in objects:
            data_object.created_by = new_user
            data_object.save()
            objects = data_object.get_related_objects()
            for related_object in objects:
                related_object.created_by = new_user
                related_object.save()


    def handle(self, *args, **options):
        keys = []

        with open(options['filename']) as f:
            for line in f:
                keys.append(int(line))
        if options['object_type'] == 'requirement':
            objects = Requirement.objects.filter(id__in=keys)
        elif options['object_type'] == 'data':
            objects = Data.objects.filter(id__in=keys)
        elif options['object_type'] == 'dataprovider':
            objects = DataProvider.objects.filter(id__in=keys)
        self.transfer_ownership_on_objects(objects, **options)