from datetime import datetime

from reportlab.lib.colors import HexColor, red, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.platypus import (
    Paragraph,
    PageBreak,
    Table,
    TableStyle,
)

from insitu.models import (
    Data,
)
from insitu.views._reports.base import BaseExcelMixin, BasePDFMixin, VerticalParagraph
from picklists.models import Country


class CountryReportExcelMixin(BaseExcelMixin):
    def set_formats(self, workbook):
        self.merge_format_light = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#e2efd9",
                "border": 1,
                "border_color": "#808080",
            }
        )

        self.merge_format_introduction = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "#80B85F",
            }
        )
        self.merge_format = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#c5e0b3",
                "border": 1,
                "border_color": "#808080",
            }
        )

        self.merge_format_dark = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#a8d08d",
                "border": 1,
                "border_color": "#808080",
            }
        )

        self.dp_column_format = workbook.add_format(
            {
                "bold": 1,
                "align": "left",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#e2efd9",
                "border": 1,
                "border_color": "#808080",
            }
        )
        self.obs_column_format = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#c5e0b3",
                "border": 1,
                "border_color": "#808080",
            }
        )

        self.additional_column_format = workbook.add_format(
            {
                "bold": 1,
                "align": "left",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#a8d08d",
                "border": 1,
                "border_color": "#808080",
            }
        )
        self.rotated_text = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri",
                "font_size": 14,
                "text_wrap": 1,
                "font_color": "black",
                "bg_color": "#c5e0b3",
                "border": 1,
                "border_color": "#808080",
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
        self.rotated_text.set_rotation(90)

    def generate_table(self, workbook, worksheet, providers):
        worksheet.set_column("A1:A1", 30, self.dp_column_format)
        worksheet.set_column("B1:G1", 8, self.obs_column_format)
        worksheet.set_column("H1:J1", 20, self.additional_column_format)
        worksheet.merge_range(
            "A1:A2",
            "Data provider",
            self.merge_format_light,
        )
        worksheet.merge_range("B1:G1", "Observation Data Type", self.merge_format)
        worksheet.merge_range(
            "H1:J1", "Additional information", self.merge_format_dark
        )
        worksheet.set_row(1, 150)
        obs_headers = [
            "Meteorology",
            "Ocean",
            "Atmosphere",
            "Hydrology",
            "Cryosphere",
            "Terrestrial",
        ]
        worksheet.write_row("B2:G2", obs_headers, self.rotated_text)
        additional_headers = ["Data policy", "Comments"]
        worksheet.write_row("H2:J2", additional_headers, self.merge_format_dark)
        worksheet.set_default_row(hide_unused_rows=True)

        index = 2
        # flake8 things
        fl = False

        data_only_with_na_compliance = [
            x.id
            for x in Data.objects.filter(
                datarequirement__level_of_compliance_id__in=[4],
                datarequirement___deleted=False,
            )
        ]
        for dp in providers:
            requirements = [
                x.requirements.all()
                for x in Data.objects.exclude(
                    id__in=data_only_with_na_compliance
                ).filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation___deleted=fl,
                )
            ]
            rg = []
            for req_list in requirements:
                rg.extend(req_list)
            rg = [x.group.name for x in rg]
            policies = (
                Data.objects.exclude(id__in=data_only_with_na_compliance)
                .filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation__provider___deleted=False,
                    dataproviderrelation___deleted=False,
                )
                .values_list("data_policy__name", flat=True)
                .distinct()
            )
            policies = [x for x in policies if x]
            row = [dp.name]
            for obs in obs_headers:
                if obs in rg:
                    row.append("X")
                else:
                    row.append(" ")
            if policies:
                row.append(" / ".join(policy for policy in policies))
            else:
                row.append("None")

            # Only write rows that have values
            try:
                row.index("X")
                worksheet.write_row(index, 0, row)
                index += 1
            except ValueError:
                continue

    def generate_header_sheet(self, workbook, worksheet):
        country_name = Country.objects.get(code=self.country_code).name
        worksheet.set_column("A1:D1", 50)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 20)
        worksheet.set_row(3, 20)
        worksheet.merge_range(
            "A1:D1",
            "Copernicus In Situ Component Information System - "
            "managed by the European Environment Agency",
            self.merge_format_introduction,
        )
        worksheet.merge_range(
            "A2:D2",
            "Country Report for {} - Observations".format(country_name),
            self.merge_format_introduction,
        )

        worksheet.merge_range(
            "A3:D3",
            f"Produced on {datetime.now():%d %B %Y}",
            self.merge_format_introduction,
        )
        worksheet.merge_range("A5:D5", "", self.format_rows_introduction)
        bold = workbook.add_format({"bold": True})
        worksheet.set_row(5, 560)
        superscript = workbook.add_format({"font_script": 1})
        worksheet.write_rich_string(
            "A5",
            "The European Environment Agency (EEA) is entrusted with cross-cutting ",
            "coordination of the Copernicus’ access to in situ data, in order ",
            "to provide \n Entrusted Entities with harmonized and, in ",
            "particular, cross-cutting information about in situ data ",
            "requirements and gaps. \n\n",
            "The Copernicus In Situ Information System CIS",
            superscript,
            "2 ",
            "(https://cis2.eea.europa.eu) aims to provide a complete ",
            "overview of requirements, gaps and data relevant to all ",
            "Copernicus services. CIS² links the in situ requirements\n "
            "specified by the Entrusted Entities to Copernicus products, ",
            "in situ datasets, and data providers in order to provide a clear "
            "picture of what data is already used\n and what would be needed ",
            "to deliver improved and more reliable products and monitoring ",
            "services. \n\n The Country Report provides an overview of ",
            "national organisations which are providing in situ observations ",
            "data to support Copernicus products. In-Situ observations are\n ",
            "non-satellite measurements of physical parameters.",
            " Observations  are either direct measurements of properties ",
            "like temperature, wind, ozone, air quality, vegetation\n",
            " properties, ocean salinity or  ground based remote sensing data ",
            "like soundings of the atmospheric composition. Observations are ",
            "provided to Copernicus either as\n individual datasets ",
            "or aggregated into gridded 2- or 3- dimensional analysis ",
            "fields. \n\n Organisations are listed across two categories \n\n",
            "    • ",
            bold,
            "Data Providers ",
            "(listed in The report is based fully on the CIS2 database content. ",
            "The CIS² database also contains similar information regarding ",
            "geospatial data, but these are not included in this country report. ",
            "): these are organisations based in the Country which provide ",
            " in situ observations data to support Copernicus products\n\n",
            "    • ",
            bold,
            "Data Provider Networks ",
            "(listed in Table 2): these are international networks with ",
            "members based in the Country, which provide in situ observations ",
            "data to support Copernicus products.\n\n ",
            "The report is based fully on the CIS2 database content. The CIS",
            superscript,
            "2",
            "database also contains similar information regarding geospatial ",
            "data, but these are not included in this country report. ",
            self.format_rows_introduction,
        )

    def generate_table_networks(self, workbook, worksheet, providers):
        worksheet.set_column("A1:A1", 30, self.dp_column_format)
        worksheet.set_column("B1:B1", 30, self.dp_column_format)
        worksheet.set_column("C1:H1", 8, self.obs_column_format)
        worksheet.set_column("I1:K1", 20, self.additional_column_format)
        worksheet.merge_range(
            "A1:A2",
            "Data provider",
            self.merge_format_light,
        )
        worksheet.merge_range("B1:B2", "Members", self.merge_format_light)
        worksheet.merge_range("C1:H1", "Observation Data Type", self.merge_format)
        worksheet.merge_range(
            "I1:K1", "Additional information", self.merge_format_dark
        )
        worksheet.set_row(1, 150)
        obs_headers = [
            "Meteorology",
            "Ocean",
            "Atmosphere",
            "Hydrology",
            "Cryosphere",
            "Terrestrial",
        ]
        worksheet.write_row("C2:H2", obs_headers, self.rotated_text)
        additional_headers = ["Data policy", "Comments"]
        worksheet.write_row("I2:K2", additional_headers, self.merge_format_dark)
        worksheet.set_default_row(hide_unused_rows=True)

        index = 2
        # flake8 things
        fl = False

        data_only_with_na_compliance = [
            x.id
            for x in Data.objects.filter(
                datarequirement__level_of_compliance_id__in=[4],
                datarequirement___deleted=False,
            )
        ]
        for dp in providers:
            members = [
                x.name
                for x in dp.members.filter(
                    _deleted=False, countries__code__in=[self.country_code]
                )
            ]
            requirements = [
                x.requirements.all()
                for x in Data.objects.exclude(
                    id__in=data_only_with_na_compliance
                ).filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation___deleted=fl,
                )
            ]
            rg = []
            for req_list in requirements:
                rg.extend(req_list)
            rg = [x.group.name for x in rg]

            policies = (
                Data.objects.exclude(id__in=data_only_with_na_compliance)
                .filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation__provider___deleted=False,
                    dataproviderrelation___deleted=False,
                )
                .values_list("data_policy__name", flat=True)
                .distinct()
            )
            policies = [x for x in policies if x]
            row = [dp.name, ""]
            for obs in obs_headers:
                if obs in rg:
                    row.append("X")
                else:
                    row.append(" ")
            if policies:
                row.append(" / ".join(policy for policy in policies))
            else:
                row.append("None")

            # Only write rows that have values
            try:
                row.index("X")
                merge = 1
                if len(members) > 1:
                    merge = len(members)
                if merge > 1:
                    worksheet.merge_range(
                        index,
                        0,
                        index + merge - 1,
                        0,
                        "",
                    )
                    for limit in range(2, 11):
                        worksheet.merge_range(
                            index, limit, index + merge - 1, limit, ""
                        )
                for num, member in enumerate(members):
                    worksheet.write(index + num, 1, member)
                worksheet.write_row(index, 0, row)
                index += merge
            except ValueError:
                continue

    def generate_worksheets(self, workbook, data=None):
        worksheet = workbook.add_worksheet("Introduction")
        self.generate_header_sheet(workbook, worksheet)
        worksheet = workbook.add_worksheet("Data provider organisations")
        self.generate_table(workbook, worksheet, self.dataproviders)
        worksheet = workbook.add_worksheet("Data provider networks")
        self.generate_table_networks(workbook, worksheet, self.dataproviders_networks)


class CountryReportPDFMixin(BasePDFMixin):
    def set_styles(self):
        styles = getSampleStyleSheet()
        self.introduction_text_header = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            textColor="#80B85F",
            leading=20,
            alignment=TA_CENTER,
        )
        self.introduction_text_subheader = ParagraphStyle(
            name="SubHeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=14,
            textColor="#80B85F",
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=60,
        )
        self.introduction_text_paragraph = ParagraphStyle(
            name="RowStyle",
            fontSize=12,
            spaceAfter=10,
            spaceBefore=0,
            leftIndent=70,
            rightIndent=70,
            alignment=TA_JUSTIFY,
        )
        self.introduction_text_paragraph_bullet_list = ParagraphStyle(
            name="RowStyle",
            fontSize=12,
            spaceAfter=10,
            spaceBefore=0,
            leftIndent=100,
            rightIndent=70,
            alignment=TA_JUSTIFY,
        )
        self.dp_column = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            textColor=black,
            leading=20,
            alignment=TA_CENTER,
        )
        self.dp_data_column = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=12,
            textColor=black,
            leading=20,
            alignment=TA_LEFT,
        )
        self.dp_members_data_column = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=12,
            textColor=black,
            leading=20,
            wordWrap="LTR",
            alignment=TA_LEFT,
        )
        self.obs_column = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=12,
            textColor=black,
            leading=20,
            alignment=TA_CENTER,
        )
        self.add_column = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            textColor=black,
            leading=20,
            alignment=TA_CENTER,
        )
        self.add_column_data = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            textColor=black,
            leading=20,
            alignment=TA_LEFT,
        )
        self.table_header_style = ParagraphStyle(
            name="TableHeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=red,
            leading=20,
        )

    def generate_text(self):
        data = []
        country_name = Country.objects.get(code=self.country_code).name
        data.append(
            Paragraph(
                "Copernicus In Situ Component Information System - managed by "
                "the European Environment Agency",
                self.introduction_text_header,
            )
        )
        data.append(
            Paragraph(
                f"Country Report for {country_name} - Observations",
                self.introduction_text_header,
            )
        )
        data.append(
            Paragraph(
                f"Produced on {datetime.now():%d %B %Y}",
                self.introduction_text_subheader,
            )
        )
        data.append(
            Paragraph(
                "The European Environment Agency (EEA) is entrusted with cross-cutting "
                "coordination of the Copernicus’ access to in situ data, in order to "
                "provide Entrusted Entities with harmonized and, in particular, "
                "cross-cutting information about in situ data requirements and gaps.",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "The Copernicus In Situ Information System CIS² ("
                "<link href='https://cis2.eea.europa.eu' color='blue'>"
                "https://cis2.eea.europa.eu </link>) aims to provide a complete "
                "overview of requirements, gaps and data relevant to all Copernicus "
                "services. CIS² links the in situ requirements specified by the "
                "Entrusted Entities to Copernicus products, in situ datasets, "
                "and data providers in order to provide a clear picture of what "
                "data is already used and what would be needed to deliver improved "
                "and more reliable products and monitoring services.",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "The Country Report provides an overview of national organisations "
                "which are providing in situ observations data to support Copernicus "
                "products. In-Situ observations are non-satellite measurements of "
                "physical parameters. Observations are either direct measurements of "
                "properties like temperature, wind, ozone, air quality, vegetation "
                "properties, ocean salinity or ground based remote sensing data like "
                "soundings of the atmospheric composition. Observations are provided "
                "to Copernicus either as individual datasets or aggregated into "
                "gridded 2- or 3- dimensional analysis fields.",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "Organisations are listed across two categories",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "- <strong>Data Providers</strong> (listed in The report is "
                "based fully on the CIS2 database content. The CIS² database "
                "also contains similar information regarding geospatial data, "
                "but these are not included in this country report.): these are "
                "organisations based in the Country which provide in situ "
                "observations data to support Copernicus products",
                self.introduction_text_paragraph_bullet_list,
            )
        )
        data.append(
            Paragraph(
                " - <strong>Data Provider Networks</strong> (listed in Table"
                " 2): these are international networks with members based in "
                "the Country, which provide in situ observations data to "
                "support Copernicus products.",
                self.introduction_text_paragraph_bullet_list,
            )
        )

        data.append(
            Paragraph(
                "The report is based fully on the CIS² database content. The CIS² "
                "database also contains similar information regarding geospatial "
                "data, but these are not included in this country report.",
                self.introduction_text_paragraph,
            )
        )
        return data

    def generate_table_pdf(self, providers):
        obs_headers = [
            "Meteorology",
            "Ocean",
            "Atmosphere",
            "Hydrology",
            "Cryosphere",
            "Terrestrial",
        ]
        data = [
            [
                Paragraph("Data provider", self.dp_column),
                Paragraph("Observation Data Type", self.obs_column),
                "",
                "",
                "",
                "",
                "",
                Paragraph("Additional information", self.add_column),
                "",
            ],
            [
                "",
                VerticalParagraph(obs_headers[0]),
                VerticalParagraph(obs_headers[1]),
                VerticalParagraph(obs_headers[2]),
                VerticalParagraph(obs_headers[3]),
                VerticalParagraph(obs_headers[4]),
                VerticalParagraph(obs_headers[5]),
                Paragraph("Data policy", self.add_column),
                Paragraph("Comments", self.add_column),
            ],
        ]

        fl = False
        data_only_with_na_compliance = [
            x.id
            for x in Data.objects.filter(
                datarequirement__level_of_compliance_id__in=[4],
                datarequirement___deleted=False,
            )
        ]
        for dp in providers:
            requirements = [
                x.requirements.all()
                for x in Data.objects.exclude(
                    id__in=data_only_with_na_compliance
                ).filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation___deleted=fl,
                )
            ]
            rg = []
            for req_list in requirements:
                rg.extend(req_list)
            rg = [x.group.name for x in rg]

            policies = (
                Data.objects.exclude(id__in=data_only_with_na_compliance)
                .filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation__provider___deleted=False,
                    dataproviderrelation___deleted=False,
                )
                .values_list("data_policy__name", flat=True)
                .distinct()
            )
            policies = [x for x in policies if x]
            row = []
            row.append([Paragraph(dp.name, self.dp_data_column)])
            for obs in obs_headers:
                if obs in rg:
                    row.append(Paragraph("X", self.obs_column))
                else:
                    row.append("")

            if policies:
                row.append(
                    Paragraph(
                        " / ".join(policy for policy in policies),
                        self.add_column_data,
                    )
                )
            else:
                row.append(
                    Paragraph("None", self.add_column_data),
                )

            row.append("")

            # Only write rows that have values
            for cell in row:
                if isinstance(cell, Paragraph):
                    if cell.text == "X":
                        data.append(row)
                        break

        style = [
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#808080")),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#e2efd9")),
            ("BACKGROUND", (1, 0), (6, -1), HexColor("#c5e0b3")),
            ("BACKGROUND", (7, 0), (8, -1), HexColor("#a8d08d")),
            ("SPAN", (0, 0), (0, 1)),
            ("SPAN", (1, 0), (6, 0)),
            ("SPAN", (7, 0), (8, 0)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        t = Table(
            data, colWidths=[200, 30, 30, 30, 30, 30, 30, 150, 200], repeatRows=1
        )
        t.setStyle(TableStyle(style))
        return t

    def generate_table_members_pdf(self, providers):
        obs_headers = [
            "Meteorology",
            "Ocean",
            "Atmosphere",
            "Hydrology",
            "Cryosphere",
            "Terrestrial",
        ]
        data = [
            [
                Paragraph("Data provider", self.dp_column),
                Paragraph("Members", self.dp_column),
                Paragraph("Observation Data Type", self.obs_column),
                "",
                "",
                "",
                "",
                "",
                Paragraph("Additional information", self.add_column),
                "",
            ],
            [
                "",
                "",
                VerticalParagraph(obs_headers[0]),
                VerticalParagraph(obs_headers[1]),
                VerticalParagraph(obs_headers[2]),
                VerticalParagraph(obs_headers[3]),
                VerticalParagraph(obs_headers[4]),
                VerticalParagraph(obs_headers[5]),
                Paragraph("Data policy", self.add_column),
                Paragraph("Comments", self.add_column),
            ],
        ]

        fl = False
        span_for_merging = []
        index = 0
        data_only_with_na_compliance = [
            x.id
            for x in Data.objects.filter(
                datarequirement__level_of_compliance_id__in=[4],
                datarequirement___deleted=False,
            )
        ]
        for dp in providers:
            members = [
                x.name
                for x in dp.members.filter(
                    _deleted=False, countries__code__in=[self.country_code]
                )
            ]

            requirements = [
                x.requirements.all()
                for x in Data.objects.exclude(
                    id__in=data_only_with_na_compliance
                ).filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation___deleted=fl,
                )
            ]
            rg = []
            for req_list in requirements:
                rg.extend(req_list)
            rg = [x.group.name for x in rg]

            policies = (
                Data.objects.exclude(id__in=data_only_with_na_compliance)
                .filter(
                    dataproviderrelation__provider=dp,
                    dataproviderrelation__provider___deleted=False,
                    dataproviderrelation___deleted=False,
                )
                .values_list("data_policy__name", flat=True)
                .distinct()
            )
            policies = [x for x in policies if x]
            row = []
            row.append([Paragraph(dp.name, self.dp_data_column)])
            if not members:
                row.append([Paragraph("", self.dp_data_column)])
            if len(members) > 0:
                row.append([Paragraph(members[0], self.dp_data_column)])
            for obs in obs_headers:
                if obs in rg:
                    row.append(Paragraph("X", self.obs_column))
                else:
                    row.append("")

            if policies:
                row.append(
                    Paragraph(
                        " / ".join(policy for policy in policies),
                        self.add_column_data,
                    )
                )
            else:
                row.append(
                    Paragraph("None", self.add_column_data),
                )

            row.append("")

            # Only write rows that have values
            for cell in row:
                if isinstance(cell, Paragraph):
                    if cell.text == "X":
                        data.append(row)
                        index += 1
                        if len(members) > 1:
                            span_for_merging.append(
                                ("SPAN", (0, index + 1), (0, index + len(members))),
                            )

                            for column_index in range(2, 10):
                                span_for_merging.append(
                                    (
                                        "SPAN",
                                        (column_index, index + 1),
                                        (column_index, index + len(members)),
                                    ),
                                )

                            for member in members[1:]:
                                index += 1
                                data.append(
                                    [
                                        "",
                                        Paragraph(member, self.dp_data_column),
                                        "",
                                        "",
                                        "",
                                        "",
                                    ]
                                )
                        break
        style = [
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#808080")),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#e2efd9")),
            ("BACKGROUND", (1, 0), (7, -1), HexColor("#c5e0b3")),
            ("BACKGROUND", (8, 0), (9, -1), HexColor("#a8d08d")),
            ("SPAN", (0, 0), (0, 1)),
            ("SPAN", (1, 0), (1, 1)),
            ("SPAN", (2, 0), (7, 0)),
            ("SPAN", (8, 0), (9, 0)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        style.extend(span_for_merging)
        t = Table(
            data, colWidths=[200, 150, 30, 30, 30, 30, 30, 30, 150, 100], repeatRows=1
        )
        t.setStyle(TableStyle(style))
        return t

    def generate_pdf_file(self, menu_pdf):
        self.set_styles()
        elements = []
        text = self.generate_text()
        elements.extend(text)
        elements.append(PageBreak())
        elements.extend(
            [
                Paragraph(
                    "Organisations",
                    self.table_header_style,
                ),
            ]
        )
        table1 = self.generate_table_pdf(self.dataproviders)
        elements.append(table1)

        elements.append(PageBreak())
        elements.extend(
            [
                Paragraph(
                    "Networks",
                    self.table_header_style,
                ),
            ]
        )

        table2 = self.generate_table_members_pdf(self.dataproviders_networks)
        elements.append(table2)
        menu_pdf.build(elements)
