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

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 20)
        worksheet.set_column("B1:B1", 35)
        worksheet.set_column("C1:C1", 35)
        worksheet.set_column("D1:D1", 20)
        worksheet.set_column("E1:E1", 15)
        worksheet.set_column("F1:F1", 60)
        worksheet.set_column("G1:G1", 50)
        worksheet.set_row(0, 50)
        worksheet.set_row(1, 40)
        worksheet.merge_range("A1:G1", "Data Networks report", self.format_header)
        headers = [
            "Network Arconym",
            "Network Name",
            "CIS² Data Provider record link",
            "Country",
            "Member ID",
            "Member Name",
            "Member record link",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)

        self.networks = DataProvider.objects.filter(id__in=self.ACCEPTED_NETWORKS_IDS)

        network_index = 2
        for network in self.networks:
            network_url = self.request.build_absolute_uri(
                reverse("provider:detail", kwargs={"pk": network.id})
            )
            country_index = network_index
            if self.country_code:
                country_objects = network.countries.filter(
                    code=self.country_code
                ).order_by("name")
            else:
                country_objects = network.countries.order_by("name")
            for country_object in country_objects:
                member_index = country_index
                for member in network.members.filter(countries__in=[country_object]):
                    worksheet.write_row(
                        member_index,
                        4,
                        [
                            member.id,
                            member.name,
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
                        3,
                        [country_object.name, "", "", ""],
                        self.format_rows,
                    )

                elif member_index == country_index + 1:
                    worksheet.write_row(
                        country_index, 3, [country_object.name], self.format_rows
                    )
                    country_index = member_index
                else:
                    worksheet.merge_range(
                        country_index,
                        3,
                        member_index - 1,
                        3,
                        country_object.name,
                        self.format_rows,
                    )
                    country_index = member_index
            if country_index == network_index:
                worksheet.write_row(
                    network_index,
                    0,
                    [
                        network.details.first().acronym,
                        network.name,
                        network_url,
                        "",
                        "",
                        "",
                        "",
                    ],
                    self.format_rows,
                )
                network_index = country_index
            elif country_index == network_index + 1:
                worksheet.write_row(
                    network_index,
                    0,
                    [network.details.first().acronym, network.name, network_url],
                    self.format_rows,
                )
                network_index = country_index
            else:
                worksheet.merge_range(
                    network_index,
                    0,
                    country_index - 1,
                    0,
                    network.details.first().acronym,
                    self.format_rows,
                )
                worksheet.merge_range(
                    network_index,
                    1,
                    country_index - 1,
                    1,
                    network.name,
                    self.format_rows,
                )
                worksheet.merge_range(
                    network_index,
                    2,
                    country_index - 1,
                    2,
                    network_url,
                    self.format_rows,
                )
                network_index = country_index

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("TABLE 1")
        self.generate_table_1(workbook, worksheet)
