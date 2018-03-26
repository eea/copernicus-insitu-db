from django.core.management.base import BaseCommand
from django.db import IntegrityError
from insitu.models import User, Team


class Command(BaseCommand):
    help = 'Create team for each user.'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            try:
                Team.objects.create(user=user)
            except IntegrityError:
                pass
