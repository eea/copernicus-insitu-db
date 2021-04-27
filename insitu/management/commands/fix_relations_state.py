from django.core.management.base import BaseCommand

from insitu.models import Requirement


class Command(BaseCommand):
    help = "Command to remove links that where created by mistake."

    def handle(self, *args, **options):
        requirements = Requirement.objects.all()

        for requirement in requirements:
            for product_req in requirement.product_requirements.all():
                product_req.state = requirement.state
                product_req.save()
            for data_req in requirement.datarequirement_set.all():
                data_req.state = requirement.state
                data_req.save()
