from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from explorer.models import Query

from insitu.management.commands.base.base_generate_special_reports import ExcelExporterWriteFile


class Command(BaseCommand):
    help = 'Command to generate the special reports from django queries.'

    def handle(self, *args, **options):
        query = get_object_or_404(Query, pk=11)
        exporter = ExcelExporterWriteFile(query)
        exporter._get_output(query, path='/var/local/static/sheets/Special_report_1.xlsx')

        query = get_object_or_404(Query, pk=12)
        exporter = ExcelExporterWriteFile(query)
        exporter._get_output(query, path='/var/local/static/sheets/Special_report_2.xlsx')
