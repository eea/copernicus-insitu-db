from django.urls import reverse

from insitu.models import DataProvider


class DataProviderNetworkReportExcelMixin:
    def set_formats(self, workbook):
        self.merge_format = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "#00B050",
            }
        )

        self.format_header = workbook.add_format(
            {
                "bold": 1,
                "align": "left",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "font_color": "red",
            }
        )

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

        self.format_rows_introduction = workbook.add_format(
            {
                "align": "justify",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 12,
                "text_wrap": True,
            }
        )

    def generate_rows_for_root_entries(self, worksheet, entries, entries_index):
        for entry in entries:
            entry_details = entry.details.first()
            entry_url = self.request.build_absolute_uri(
                reverse("provider:detail", kwargs={"pk": entry.id})
            )
            country_index = entries_index
            if self.country_codes:
                country_objects = entry.countries.filter(
                    code__in=self.country_codes
                ).order_by("name")
            else:
                country_objects = entry.countries.order_by("name")
            for country_object in country_objects:
                member_index = country_index
                for member in entry.members.filter(countries__in=[country_object]):
                    member_details = member.details.first()
                    worksheet.write_row(
                        member_index,
                        6,
                        [
                            member.id,
                            member.name,
                            member.native_name,
                            member_details.website,
                            self.request.build_absolute_uri(
                                reverse("provider:detail", kwargs={"pk": member.id})
                            ),
                        ],
                        self.format_rows,
                    )
                    member_index += 1
                if member_index == country_index:
                    worksheet.write_row(
                        country_index,
                        5,
                        [country_object.name, "", "", "", "", ""],
                        self.format_rows,
                    )
                    country_index += 1

                elif member_index == country_index + 1:
                    worksheet.write_row(
                        country_index, 5, [country_object.name], self.format_rows
                    )
                    country_index = member_index
                else:
                    worksheet.merge_range(
                        country_index,
                        5,
                        member_index - 1,
                        5,
                        country_object.name,
                        self.format_rows,
                    )
                    country_index = member_index
            if country_index == entries_index:
                worksheet.write_row(
                    entries_index,
                    0,
                    [
                        entry_details.acronym,
                        entry.name,
                        entry.native_name,
                        entry_details.website,
                        entry_url,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                    self.format_rows,
                )
                entries_index += 1
            elif country_index == entries_index + 1:
                worksheet.write_row(
                    entries_index,
                    0,
                    [
                        entry_details.acronym,
                        entry.name,
                        entry.native_name,
                        entry_details.website,
                        entry_url,
                    ],
                    self.format_rows,
                )
                entries_index = country_index
            else:
                worksheet.merge_range(
                    entries_index,
                    0,
                    country_index - 1,
                    0,
                    entry_details.acronym,
                    self.format_rows,
                )
                worksheet.merge_range(
                    entries_index,
                    1,
                    country_index - 1,
                    1,
                    entry.name,
                    self.format_rows,
                )
                worksheet.merge_range(
                    entries_index,
                    2,
                    country_index - 1,
                    2,
                    entry.native_name,
                    self.format_rows,
                )
                worksheet.merge_range(
                    entries_index,
                    3,
                    country_index - 1,
                    3,
                    entry_details.website,
                    self.format_rows,
                )
                worksheet.merge_range(
                    entries_index,
                    4,
                    country_index - 1,
                    4,
                    entry_url,
                    self.format_rows,
                )
                entries_index = country_index
        return entries_index

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 30)
        worksheet.set_column("B1:B1", 35)
        worksheet.set_column("C1:C1", 35)
        worksheet.set_column("D1:D1", 35)
        worksheet.set_column("E1:E1", 35)
        worksheet.set_column("F1:F1", 10)
        worksheet.set_column("G1:G1", 10)
        worksheet.set_column("H1:H1", 60)
        worksheet.set_column("I1:I1", 60)
        worksheet.set_column("J1:J1", 35)
        worksheet.set_column("K1:K1", 35)
        worksheet.set_row(0, 50)
        worksheet.set_row(1, 40)
        worksheet.write_row("A1", ["Networks"], self.format_header)
        # worksheet.merge_range("A1:G1", "Networks", self.format_header)
        headers = [
            "Network Acronym",
            "Network Name",
            "Network native name",
            "Network website",
            "CIS² Data Provider record link",
            "Country",
            "Member ID",
            "Member Name",
            "Member Native name",
            "Member website",
            "Member record link",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)

        networks = DataProvider.objects.filter(id__in=self.ACCEPTED_NETWORKS_IDS)
        entries_index = self.generate_rows_for_root_entries(worksheet, networks, 2)
        research_infrastructures = DataProvider.objects.filter(
            id__in=self.ACCEPTED_RESEARCH_INFRASTRUCTURES_IDS
        )
        worksheet.set_row(entries_index, 40)
        worksheet.write_row(
            entries_index, 0, ["Research Infrastructures"], self.format_header
        )
        entries_index += 1
        worksheet.write_row(entries_index, 0, headers, self.format_cols_headers)
        self.generate_rows_for_root_entries(
            worksheet, research_infrastructures, entries_index + 1
        )

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("TABLE 1")
        self.generate_table_1(workbook, worksheet)
