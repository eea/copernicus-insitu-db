from django.core.management.base import BaseCommand
from insitu.models import Requirement


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
