import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from insitu.models import LoggedAction
from datetime import datetime


class Command(BaseCommand):
    help = "Import logs from CSV file"

    def handle(self, *args, **options):
        with open(settings.LOGGING_CSV_PATH, "r+") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                dt_obj = datetime.strptime(row[0], "%d %B %Y %H:%M")
                LoggedAction.objects.create(
                    logged_date=dt_obj,
                    user=row[1],
                    action=row[2],
                    target_type=row[3],
                    id_target=row[4],
                    extra=row[5:6] if row[5:6] else None
                )
