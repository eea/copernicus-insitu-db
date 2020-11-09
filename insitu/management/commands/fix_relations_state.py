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
            for product_req in requirement.productrequirement_set.all():
                product_req.state = requirement.state
                product_req.save()
            for data_req in requirement.datarequirement_set.all():
                data_req.state = requirement.state
                data_req.save()
