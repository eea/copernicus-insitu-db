from datetime import datetime
import json
import os
import uuid
import xlsxwriter

from explorer.exporters import ExcelExporter


class ExcelExporterWriteFile(ExcelExporter):

    def _get_output(self, query, path,  **kwargs):
        res = query.execute_query_only()

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        wb = xlsxwriter.Workbook(path, {'constant_memory': True})
        ws = wb.add_worksheet(name=self._format_title())
        row = 0
        col = 0
        header_style = wb.add_format({'bold': True})
        for header in res.header_strings:
            ws.write(row, col, header, header_style)
            col += 1
        row = 1
        col = 0
        for data_row in res.data:
            for data in data_row:
                if isinstance(data, datetime) or isinstance(data, uuid.UUID):
                    data = str(data)
                if isinstance(data, dict) or isinstance(data, list):
                    data = json.dumps(data)
                ws.write(row, col, data)
                col += 1
            row += 1
            col = 0
        wb.close()
