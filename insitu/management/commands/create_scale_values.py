from django.core.management.base import BaseCommand

from insitu.models import Requirement, Metric


class Command(BaseCommand):
    help = "Command to remove links that where created by mistake."

    def handle(self, *args, **options):
        requirements = Requirement.objects.really_all()
        for requirement in requirements:
            if requirement.scale is not None:
                scale = requirement.scale
                scale.save()
            else:
                metric = Metric.objects.create(
                    threshold="",
                    breakthrough="",
                    goal="",
                    created_by=requirement.created_by,
                )
                requirement.scale = metric
                requirement.save()
