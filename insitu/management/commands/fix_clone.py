
from django.core.management.base import BaseCommand, CommandError
from insitu.models import Requirement


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        requirements = Requirement.objects.all()
        for requirement in requirements:
            requirement.name = requirement.name.strip()
            requirement.note = requirement.note.strip()
            requirement.uncertainty.threshold = requirement.uncertainty.threshold.strip()
            requirement.uncertainty.breakthrough = requirement.uncertainty.breakthrough.strip()
            requirement.uncertainty.goal = requirement.uncertainty.goal.strip()

            requirement.update_frequency.threshold = requirement.update_frequency.threshold.strip()
            requirement.update_frequency.breakthrough = requirement.update_frequency.breakthrough.strip()
            requirement.update_frequency.goal = requirement.update_frequency.goal.strip()

            requirement.timeliness.threshold = requirement.timeliness.threshold.strip()
            requirement.timeliness.breakthrough = requirement.timeliness.breakthrough.strip()
            requirement.timeliness.goal = requirement.timeliness.goal.strip()

            requirement.horizontal_resolution.threshold = requirement.horizontal_resolution.threshold.strip()
            requirement.horizontal_resolution.breakthrough = requirement.horizontal_resolution.breakthrough.strip()
            requirement.horizontal_resolution.goal = requirement.horizontal_resolution.goal.strip()

            requirement.vertical_resolution.threshold = requirement.vertical_resolution.threshold.strip()
            requirement.vertical_resolution.breakthrough = requirement.vertical_resolution.breakthrough.strip()
            requirement.vertical_resolution.goal = requirement.vertical_resolution.goal.strip()
            requirement.save()
