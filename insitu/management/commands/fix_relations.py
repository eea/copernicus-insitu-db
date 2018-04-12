from django.core.management.base import BaseCommand
from insitu.models import  Data, DataProvider, Requirement


class Command(BaseCommand):
    help = 'Use in case the relation state gets out of sync from the requirement state.'

    def handle(self, *args, **options):
        requirements = Requirement.objects.all()
        faulty_requirements = [
            requirement for requirement in requirements if [
                rel for rel in requirement.productrequirement_set.all()
                if rel.state != requirement.state
            ] or [
                rel for rel in requirement.datarequirement_set.all()
                if rel.state != requirement.state
            ] or
            requirement.uncertainty.state != requirement.state or
            requirement.update_frequency.state != requirement.state or
            requirement.timeliness.state != requirement.state or
            requirement.horizontal_resolution.state != requirement.state or
            requirement.vertical_resolution.state != requirement.state
        ]

        print('Relations will be fixed for requirements:..')
        for requirement in faulty_requirements:
            print(requirement.name)
            for rel in requirement.productrequirement_set.all():
                if rel.state != requirement.state:
                    rel.state = requirement.state
                    rel.save()
            for rel in requirement.datarequirement_set.all():
                if rel.state != requirement.state:
                    rel.state = requirement.state
                    rel.save()
            if requirement.uncertainty.state != requirement.state:
                requirement.uncertainty.state = requirement.state
                requirement.uncertainty.save()
            if requirement.update_frequency.state != requirement.state:
                requirement.update_frequency.state = requirement.state
                requirement.update_frequency.save()
            if requirement.timeliness.state != requirement.state:
                requirement.timeliness.state = requirement.state
                requirement.timeliness.save()
            if requirement.horizontal_resolution.state != requirement.state:
                requirement.horizontal_resolution.state = requirement.state
                requirement.horizontal_resolution.save()
            if requirement.vertical_resolution.state != requirement.state:
                requirement.vertical_resolution.state = requirement.state
                requirement.vertical_resolution.save()

        data_objects = Data.objects.all()
        faulty_data = [
            data for data in data_objects if [
                rel for rel in data.dataproviderrelation_set.all()
                if rel.state != data.state
            ]
        ]
        print('Relations will be fixed for data:..')
        for data in faulty_data:
            print(data.name)
            for rel in data.dataproviderrelation_set.all():
                if rel.state != data.state:
                    rel.state = data.state
                    rel.save()


        data_providers = DataProvider.objects.all()
        faulty_data_providers = [
            data_provider for data_provider in data_providers if [
                rel for rel in data_provider.details.all()
                if rel.state != data_provider.state
            ]
        ]

        print('Relations will be fixed for data provider:..')
        for data_provider in faulty_data_providers:
            print(data_provider.name)
            for rel in data_provider.details.all():
                if rel.state != data_provider.state:
                    rel.state = data_provider.state
                    rel.save()
