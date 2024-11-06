from django.apps import apps

from insitu.views._reports.base import BaseExcelMixin


class EntriesStateReportExcelMixin(BaseExcelMixin):
    def set_formats(self, workbook):

        self.format_cols_headers = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 12,
                "font_color": "#0070C0",
                "bg_color": "#8CA9D7",
                "border": 1,
            }
        )

        self.format_rows = workbook.add_format(
            {
                "align": "left",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 12,
                "text_wrap": True,
                "border": 1,
            }
        )

    def generate_table_1(self, workbook, worksheet, entries):
        worksheet.set_column("A1:A1", 30)
        worksheet.set_column("B1:B1", 35)
        worksheet.set_column("C1:C1", 35)
        worksheet.set_column("D1:D1", 35)
        worksheet.set_column("E1:E1", 35)
        headers = [
            "UID",
            "Name",
            "State",
            "Last updated",
            "URL",
        ]
        worksheet.write_row("A1", headers, self.format_cols_headers)
        for idx, entry in enumerate(entries, start=1):
            cells = [
                entry.id,
                entry.name,
                getattr(entry, "state", ""),
                getattr(entry, "updated_at", "").strftime("%Y-%m-%d %H:%M:%S"),
                self.request.build_absolute_uri(entry.get_detail_link()),
            ]
            worksheet.write_row(idx, 0, cells, self.format_rows)

    def get_entries(self):
        model = apps.get_model("insitu", self.entry_type)
        return model.objects.all().order_by("name")

    def generate_worksheets(self, workbook, data=None):
        worksheet = workbook.add_worksheet("TABLE 1")
        entries = self.get_entries()
        self.generate_table_1(workbook, worksheet, entries)
