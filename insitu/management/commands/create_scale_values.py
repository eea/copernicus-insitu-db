from datetime import datetime
import pytz

from django.core.management.base import BaseCommand
from django.utils import timezone

from insitu.models import  Requirement, Metric


class Command(BaseCommand):
    help = 'Command to remove links that where created by mistake.'

    def handle(self, *args, **options):
        requirements = Requirement.objects.really_all()
        for requirement in requirements:
            metric = Metric.objects.create(
                threshold='',
                breakthrough='',
                goal='',
                created_by=requirement.created_by
            )
            requirement.scale = metric
            requirement.save()
