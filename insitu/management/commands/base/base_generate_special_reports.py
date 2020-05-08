from datetime import datetime
import json
import os
import uuid
import xlsxwriter
from django.db import connection

from explorer.exporters import ExcelExporter

def result_iter(cursor, arraysize=2000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        yield results

class ExcelExporterWriteFile(ExcelExporter):

    def _get_output(self, query, path,  **kwargs):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        wb = xlsxwriter.Workbook(path, {'constant_memory': True})
        ws = wb.add_worksheet(name=self._format_title())


        with connection.cursor() as cursor:
            cursor.execute(query.sql)
            header_style = wb.add_format({'bold': True})
            columns = [col[0] for col in cursor.description]
            ws.write_row(0, 0,  columns)
            row = 1
            for result in result_iter(cursor):
                for data_row in result:
                    ws.write_row(row, 0, data_row)
                    row += 1
            wb.close()
