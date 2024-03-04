import csv

from django.core.management.base import BaseCommand

from insitu import models as insitu_models
from picklists import models as pickmodels


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("filename", nargs="+", type=str)

    def handle(self, *args, **options):
        filename = options["filename"][0]
        with open(filename, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                essential_variable_id = row["essential_variable_id"]
                requirement_id = row["requirement_id"]

                essential_variable = pickmodels.EssentialVariable.objects.filter(
                    id=essential_variable_id
                ).first()
                requirement = insitu_models.Requirement.objects.filter(
                    id=requirement_id
                ).first()
                if not essential_variable:
                    print(
                        "Essential variable {} not found".format(essential_variable_id)
                    )
                    continue
                if not requirement:
                    print("Requirement {} not found".format(requirement_id))
                    continue

                print(
                    "Adding essential variable {} to requirement {}".format(
                        essential_variable_id, requirement_id
                    )
                )
                requirement.essential_variables.add(essential_variable)
