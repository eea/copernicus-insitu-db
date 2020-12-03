from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from explorer.models import Query

from insitu.management.commands.base.base_generate_special_reports import (
    ExcelExporterWriteFile,
)


class Command(BaseCommand):
    help = "Command to generate the special reports from django queries."

    def add_arguments(self, parser):
        parser.add_argument("id", type=int)
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        query = get_object_or_404(Query, pk=options["id"])
        print("Starting generating excel for report {}".format(options["id"]))
        exporter = ExcelExporterWriteFile(query)
        exporter._get_output(
            query, path="/var/local/static/sheets/" + options["filename"]
        )
        print("Finished generating excel for report {}".format(options["id"]))
