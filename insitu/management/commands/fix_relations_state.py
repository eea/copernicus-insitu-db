from datetime import datetime
import pytz

from django.core.management.base import BaseCommand
from django.utils import timezone

from insitu.models import  Requirement, Metric


class Command(BaseCommand):
    help = 'Command to remove links that where created by mistake.'

    def handle(self, *args, **options):
        requirements = Requirement.objects.all()
        metrics = [
            'uncertainty', 'update_frequency', 'timeliness',
            'scale', 'horizontal_resolution', 'vertical_resolution'
        ]

        for requirement in requirements:
            for metric in metrics:
                metric_object = getattr(requirement, metric)
                metric_object.state = requirement.state
                metric_object.save()
