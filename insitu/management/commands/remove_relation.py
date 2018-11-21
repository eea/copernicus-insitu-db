from datetime import datetime
import pytz

from django.core.management.base import BaseCommand
from django.utils import timezone

from insitu.models import  ProductRequirement, User


class Command(BaseCommand):
    help = 'Command to remove links that where created by mistake.'

    def add_arguments(self, parser):
        parser.add_argument('users', type=str, help='First user')

    def handle(self, *args, **options):
        with open("removed_links.txt", "w" ) as f:
            timezone.now()
            from_date = datetime(2018, 11, 12, 0, 0, 0, 0, pytz.UTC)
            users = options['users'].split(',')
            for user in users:
                f.write("User {} links:\n".format(user))
                user = User.objects.filter(username=user).first()
                links_pr_req = ProductRequirement.objects.filter(created_by=user, created_at__gte=from_date)
                for link in links_pr_req:
                    f.write("Requirement: {} - Product: {}  with level_of_definition: {}, relevance: {} and criticality: {}\n".format(
                        link.requirement.name, 
                        link.product.name,
                        link.level_of_definition.name, 
                        link.relevance.name, 
                        link.criticality.name
                    ))
                    link.delete()

