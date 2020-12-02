from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from insitu.models import User, Team


class Command(BaseCommand):
    help = "Remove all relations between users."

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            try:
                team = Team.objects.get(user=user)
                team.teammates.clear()
            except ObjectDoesNotExist:
                Team.objects.create(user=user)
