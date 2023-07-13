from insitu.models import Data, Requirement, DataProvider
from django.utils.html import strip_tags
from picklists.models import Country
import datetime

from reportlab.platypus import (
    Paragraph,
    PageBreak,
    Table,
    TableStyle,
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, HexColor, red, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class ReportExcelMixin:
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
                "bg_color": "#c3d69b",
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

    def generate_header_sheet(self, workbook, worksheet):
        worksheet.set_column("A1:D1", 50)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 20)
        worksheet.set_row(3, 20)
        worksheet.merge_range(
            "A1:D1",
            "Copernicus In Situ Component Information System - "
            "managed by the European Environment Agency",
            self.merge_format,
        )
        worksheet.merge_range(
            "A3:D3",
            "Standard Report for {} Component".format(
                ", ".join([elem.name for elem in self.components])
            ),
            self.merge_format,
        )

        worksheet.merge_range(
            "A4:D4",
            "Produced on {}".format(datetime.datetime.now().strftime("%d %B %Y")),
            self.merge_format,
        )
        worksheet.merge_range("A6:D6", "", self.format_rows_introduction)
        bold = workbook.add_format({"bold": True})
        worksheet.set_row(5, 560)
        superscript = workbook.add_format({"font_script": 1})
        worksheet.write_rich_string(
            "A6",
            "The European Environment Agency (EEA) is entrusted with cross-cutting ",
            "coordination of the Copernicus In Situ Component in order to provide ",
            "Entrusted Entities with harmonized and, in particular, cross-cutting ",
            "information about in situ data requirements and gaps.\n\n",
            "The Copernicus In Situ Information System (CIS",
            superscript,
            "2",
            ") aims to provide a ",
            "complete overview of requirements, gaps and data relevant to all ",
            "Copernicus services.\n\n",
            "The Standard Report should be used in combination with the State ",
            "of Play Report that focuses on cross-cutting challenges and gaps ",
            "and made available simultaneously.\n\n",
            "CIS",
            superscript,
            "2 ",
            "links the in situ requirements specified by the Entrusted ",
            "Entities to Copernicus products, in situ datasets, and data ",
            "providers in order to provide a clear picture of ",
            bold,
            "what data is already used ",
            "and ",
            bold,
            "what would be needed to deliver improved and more reliable products ",
            "and monitoring services.\n\n",
            "CIS",
            superscript,
            "2 ",
            "shows in situ data requirements and which datasets are used ",
            "for each Copernicus Service product. For each product, datasets ",
            "are characterised in terms of:\n",
            "•",
            bold,
            "Criticality: ",
            "the importance of the requirement for the ",
            "supply of reliable products (Essential, Desirable, or Useful).\n",
            "•",
            bold,
            "Relevance: ",
            "the extent to which a dataset corresponds with the intended ",
            "purpose (product generation, calibration and validation, support of ",
            "exploitation)\n",
            "•",
            bold,
            "Compliance level: ",
            " how far the dataset meets the stated requirement ",
            "(Fully, Partially, None).\n",
            "•",
            bold,
            "Barriers: ",
            "the main reasons why a given in situ requirement is not ",
            "satisfied for the product concerned (e.g. accuracy, availability, ",
            "timeliness, update frequency, coverage).\n\n",
            "As well as demonstrating in general terms the crucial importance of ",
            "in situ data for the operation of the Copernicus Services, the ",
            "information in the database helps to identify, for example:\n",
            "    • Which datasets are in use and data providers\n",
            "    • The priority requirements for in situ data\n",
            "    • Gaps in data provision\n",
            "    • Barriers to the effective use of the data\n",
            "    • Requirements and issues which affect more than one ",
            "service component or dataset\n",
            "    • Priority areas for action to improve provision\n\n",
            "The database therefore provides an essential building block for",
            "the development of new actions to improve and promote sustainable",
            "data provision and hence effective user-driven services.\n\n",
            "This Report sets out in a systematic way the information",
            "contained in the database relating",
            "to the {} Service component.\n\n".format(
                ", ".join([elem.name for elem in self.components])
            ),
            "The CIS",
            superscript,
            "2 ",
            "database continues to evolve, and updates of this and the other CIS",
            superscript,
            "2 ",
            "Standard ",
            "Reports will be made available periodically. They will inform discussion",
            "between the EEA and the Services, and with wider stakeholders such as ",
            "regulators and data owners, contributing to identifying actions ",
            "necessary to provide improved user-driven services. It is therefore ",
            "very important that they be carefully studied so that a ",
            "shared narrative can be developed.",
            self.format_rows_introduction,
        )

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 20)
        worksheet.set_column("B1:B1", 50)
        worksheet.set_column("C1:C1", 50)
        worksheet.set_column("D1:K1", 25)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 20)
        worksheet.merge_range(
            "A1:K1", "REQUIREMENTS AND THEIR DETAILS", self.format_header
        )
        headers = [
            "REQUIREMENT UID",
            "REQUIREMENT",
            "NOTE",
            "DISSEMINATION",
            "QUALITY CONTROL",
            "GROUP",
            "UNCERTAINTY (%)",
            "UPDATE FREQUENCY",
            "TIMELINESS",
            "SCALE",
            "HORIZONTAL RESOLUTION",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)

        self.requirements = (
            Requirement.objects.filter(
                product_requirements___deleted=False,
                product_requirements__product__in=self.products,
            )
            .distinct()
            .order_by("name")
        )

        self.data = (
            Data.objects.filter(
                datarequirement___deleted=False,
                datarequirement__requirement__in=self.requirements,
            )
            .distinct()
            .order_by("name")
        )

        self.data_providers = (
            DataProvider.objects.filter(
                dataproviderrelation___deleted=False,
                dataproviderrelation__data__in=self.data,
            )
            .distinct()
            .order_by("name")
        )
        index = 2
        for requirement in self.requirements:
            data = [
                requirement.id,
                requirement.name,
                requirement.note,
                requirement.dissemination.name,
                requirement.quality_control_procedure.name,
                requirement.group.name,
                requirement.uncertainty.breakthrough,
                requirement.update_frequency.breakthrough,
                requirement.timeliness.breakthrough,
                requirement.scale.breakthrough,
                requirement.horizontal_resolution.breakthrough,
            ]
            worksheet.write_row(index, 0, data, self.format_rows)
            index += 1

    def generate_table_2(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 20)
        worksheet.set_column("B1:B1", 120)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:B1", "PRODUCTS AND THEIR DESCRIPTIONS", self.format_header
        )
        headers = ["PRODUCT", "DESCRIPTION"]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            data = [product.name, product.description]
            worksheet.write_row(index, 0, data, self.format_rows)
            index += 1

    def generate_table_3(self, workbook, worksheet):
        worksheet.set_column("A1:B1", 20)
        worksheet.set_column("C1:C1", 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:C1", "PRODUCTS AND ASSOCIATED REQUIREMENTS", self.format_header
        )
        headers = ["PRODUCT", "REQUIREMENT", "REQUIREMENT UID"]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            requirements = (
                product.product_requirements.filter(
                    _deleted=False, requirement_id__in=self.requirements
                )
                .order_by("requirement__name")
                .order_by("requirement__name")
            )
            requirement_count = requirements.count()
            if requirement_count >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + requirement_count - 1,
                    0,
                    product.name,
                    self.format_rows,
                )
                for product_requirement in requirements.all():
                    data = [
                        product_requirement.requirement.name,
                        product_requirement.requirement.id,
                    ]
                    worksheet.write_row(index, 1, data, self.format_rows)
                    index += 1
            elif requirement_count == 1:
                requirement = requirements.first().requirement
                worksheet.write_row(
                    index,
                    0,
                    [product.name, requirement.name, requirement.id],
                    self.format_rows,
                )
                index += 1
            else:
                worksheet.write_row(index, 0, [product.name, "", ""], self.format_rows)
                index += 1

    def generate_table_4(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 30)
        worksheet.set_column("B1:B1", 20)
        worksheet.set_column("C1:D1", 20)
        worksheet.set_column("E1:E1", 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:E1",
            "DATASETS AND RELATED DATA PROVIDERS PER REQUIREMENT",
            self.format_header,
        )
        headers = [
            "REQUIREMENT",
            "REQUIREMENT UID",
            "DATA",
            "DATA PROVIDER",
            "DATA PROVIDER TYPE",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        requirement_index = 2
        for requirement in self.requirements:
            data_index = requirement_index
            data_objects = (
                Data.objects.filter(
                    requirements__in=[requirement],
                    datarequirement___deleted=False,
                    datarequirement__requirement__in=self.requirements,
                )
                .distinct()
                .order_by("name")
            )
            for data_object in data_objects:
                provider_index = data_index
                for (
                    data_provider_relation
                ) in data_object.dataproviderrelation_set.filter(
                    _deleted=False, provider__in=self.data_providers
                ).order_by(
                    "provider__name"
                ):
                    data_provider = data_provider_relation.provider
                    worksheet.write_row(
                        provider_index,
                        3,
                        [
                            data_provider.name,
                            getattr(
                                getattr(
                                    data_provider.details.first(), "provider_type", ""
                                ),
                                "name",
                                "",
                            ),
                        ],
                        self.format_rows,
                    )
                    provider_index += 1
                if provider_index == data_index:
                    worksheet.write_row(
                        data_index,
                        2,
                        [data_object.name, "", ""],
                        self.format_rows,
                    )
                    data_index = provider_index
                elif provider_index == data_index + 1:
                    worksheet.write_row(
                        data_index, 2, [data_object.name], self.format_rows
                    )
                else:
                    worksheet.merge_range(
                        data_index,
                        2,
                        provider_index - 1,
                        2,
                        data_object.name,
                        self.format_rows,
                    )
                data_index = provider_index
            if data_index == requirement_index:
                worksheet.write_row(
                    requirement_index,
                    0,
                    [requirement.name, requirement.id, "", "", ""],
                    self.format_rows,
                )
                requirement_index = data_index + 1
            elif data_index == requirement_index + 1:
                worksheet.write_row(
                    requirement_index,
                    0,
                    [requirement.name, requirement.id],
                    self.format_rows,
                )
                requirement_index = data_index
            else:
                worksheet.merge_range(
                    requirement_index,
                    0,
                    data_index - 1,
                    0,
                    requirement.name,
                    self.format_rows,
                )
                worksheet.merge_range(
                    requirement_index,
                    1,
                    data_index - 1,
                    1,
                    requirement.id,
                    self.format_rows,
                )
                requirement_index = data_index

    def generate_table_5(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 50)
        worksheet.set_column("B1:B1", 60)
        worksheet.set_column("C1:F1", 18)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:F1",
            "MAIN DETAILS BETWEEN REQUIREMENTS AND PRODUCTS",
            self.format_header,
        )
        headers = [
            "PRODUCT",
            "REQUIREMENT",
            "REQUIREMENT UID",
            "BARRIER",
            "RELEVANCE",
            "CRITICALITY",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            product_merge_dimension = product.product_requirements.filter(
                requirement_id__in=self.requirements
            ).count()
            if product_merge_dimension >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + product_merge_dimension - 1,
                    0,
                    product.name,
                    self.format_rows,
                )
                for product_requirement in product.product_requirements.filter(
                    requirement_id__in=self.requirements
                ).order_by("requirement__name"):
                    data = [
                        product_requirement.requirement.name,
                        product_requirement.requirement.id,
                        "\n".join([x.name for x in product_requirement.barriers.all()]),
                        product_requirement.relevance.name,
                        product_requirement.criticality.name,
                    ]
                    worksheet.write_row(index, 1, data, self.format_rows)
                    index += 1
            elif product_merge_dimension == 1:
                product_requirement = product.product_requirements.filter(
                    requirement_id__in=self.requirements
                ).first()
                worksheet.write_row(
                    index,
                    0,
                    [
                        product.name,
                        product_requirement.requirement.name,
                        product_requirement.requirement.id,
                        "\n".join([x.name for x in product_requirement.barriers.all()]),
                        product_requirement.relevance.name,
                        product_requirement.criticality.name,
                    ],
                    self.format_rows,
                )
                index += 1
            else:
                worksheet.write_row(
                    index, 0, [product.name, "", "", "", "", ""], self.format_rows
                )
                index += 1

    def generate_table_6(self, workbook, worksheet):
        worksheet.set_column("A1:C1", 40)
        worksheet.set_column("D1:D1", 60)
        worksheet.set_column("E1:E1", 40)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:E1",
            "LEVEL OF COMPLIANCE BETWEEN DATASET AND REQUIREMENT",
            self.format_header,
        )
        headers = [
            "PRODUCT",
            "DATA",
            "REQUIREMENT",
            "REQUIREMENT UID",
            "DATA LINK NOTE",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        product_index = 2
        for product in self.products:
            requirements = [
                x.requirement
                for x in product.product_requirements.filter(
                    requirement_id__in=self.requirements
                ).order_by("requirement__name")
            ]
            data = (
                Data.objects.filter(
                    datarequirement__requirement__in=requirements,
                    datarequirement___deleted=False,
                )
                .filter(id__in=self.data)
                .distinct()
                .order_by("name")
            )
            data_index = product_index
            for data_object in data:
                data_requirement_index = data_index
                data_requirements = data_object.datarequirement_set.filter(
                    requirement_id__in=self.requirements, _deleted=False
                ).order_by("requirement__name")
                for data_requirement in data_requirements:
                    worksheet.write_row(
                        data_requirement_index,
                        2,
                        [
                            data_requirement.requirement.name,
                            data_requirement.requirement.id,
                            data_requirement.note,
                        ],
                        self.format_rows,
                    )
                    data_requirement_index += 1
                if data_index == data_requirement_index:
                    worksheet.write_row(
                        data_index, 1, [data_object.name, "", "", ""], self.format_rows
                    )
                    data_index = data_requirement_index
                elif data_requirement_index == data_index + 1:
                    worksheet.write_row(
                        data_index, 1, [data_object.name], self.format_rows
                    )
                else:
                    worksheet.merge_range(
                        data_index,
                        1,
                        data_requirement_index - 1,
                        1,
                        data_object.name,
                        self.format_rows,
                    )
                data_index = data_requirement_index
            if data_index == product_index:
                worksheet.write_row(
                    product_index, 0, [product.name, "", "", "", ""], self.format_rows
                )
                product_index = data_index + 1
            elif data_index == product_index + 1:
                worksheet.write_row(product_index, 0, [product.name], self.format_rows)
                product_index = data_index
            else:
                worksheet.merge_range(
                    product_index, 0, data_index - 1, 0, product.name, self.format_rows
                )
                product_index = data_index

    def generate_table_7(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 40)
        worksheet.set_column("B1:F1", 20)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range("A1:F1", "DATASET MAIN DETAILS", self.format_header)
        headers = [
            "DATA",
            "DATA TYPE",
            "DATA FORMAT",
            "DATA UPDATE FREQUENCY",
            "DATA AREA",
            "DATA POLICY",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for data_object in self.data:
            row_data = [
                data_object.name,
                getattr(data_object.data_type, "name", ""),
                getattr(data_object.data_format, "name", ""),
                getattr(data_object.update_frequency, "name", ""),
                getattr(data_object.area, "name", ""),
                getattr(data_object.data_policy, "name", ""),
            ]
            worksheet.write_row(index, 0, row_data, self.format_rows)
            index += 1

    def generate_table_8(self, workbook, worksheet):
        worksheet.set_column("A1:B1", 40)
        worksheet.set_column("C1:G1", 25)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:G1", "DATASETS AND RELATED DATA PROVIDERS", self.format_header
        )
        headers = [
            "DATA",
            "DATA PROVIDER",
            "DATA PROVIDER TYPE",
            "DATA PROVIDER ROLE",
            "DATA QUALITY CONTROL",
            "DATA DISSEMINATION",
            "DATA TIMELINESS",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for data_object in self.data:
            provider_count = data_object.dataproviderrelation_set.filter(
                provider__in=self.data_providers
            ).count()
            if provider_count >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + provider_count - 1,
                    0,
                    data_object.name,
                    self.format_rows,
                )
                for (
                    dataprovider_relation
                ) in data_object.dataproviderrelation_set.all().order_by(
                    "provider__name"
                ):
                    dataprovider = dataprovider_relation.provider
                    role = dataprovider_relation.get_role_display()
                    row_data = [
                        dataprovider.name,
                        getattr(
                            getattr(dataprovider.details.first(), "provider_type", ""),
                            "name",
                            "",
                        ),
                        role,
                        getattr(data_object.quality_control_procedure, "name", ""),
                        getattr(data_object.dissemination, "name", ""),
                        getattr(data_object.timeliness, "name", ""),
                    ]
                    worksheet.write_row(index, 1, row_data, self.format_rows)
                    index += 1
            elif provider_count == 1:
                dataprovider_relation = data_object.dataproviderrelation_set.first()
                dataprovider = dataprovider_relation.provider
                row_data = [
                    data_object.name,
                    dataprovider.name,
                    dataprovider_relation.get_role_display(),
                    getattr(
                        getattr(dataprovider.details.first(), "provider_type", ""),
                        "name",
                        "",
                    ),
                    getattr(data_object.quality_control_procedure, "name", ""),
                    getattr(data_object.dissemination, "name", ""),
                    getattr(data_object.timeliness, "name", ""),
                ]
                worksheet.write_row(index, 0, row_data, self.format_rows)
                index += 1
            else:
                worksheet.write_row(
                    index,
                    0,
                    [data_object.name, "", "", "", "", "", ""],
                    self.format_rows,
                )
                index += 1

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("INTRODUCTION")
        self.generate_header_sheet(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 1")
        self.generate_table_1(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 2")
        self.generate_table_2(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 3")
        self.generate_table_3(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 4")
        self.generate_table_4(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 5")
        self.generate_table_5(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 6")
        self.generate_table_6(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 7")
        self.generate_table_7(workbook, worksheet)
        worksheet = workbook.add_worksheet("TABLE 8")
        self.generate_table_8(workbook, worksheet)


class PDFExcelMixin:
    def generate_table_1_pdf(self):
        self.requirements = (
            Requirement.objects.filter(
                product_requirements___deleted=False,
                product_requirements__product__in=self.products,
            )
            .distinct()
            .order_by("name")
        )

        self.data = (
            Data.objects.filter(
                datarequirement___deleted=False,
                datarequirement__requirement__in=self.requirements,
            )
            .distinct()
            .order_by("name")
        )

        self.data_providers = (
            DataProvider.objects.filter(
                dataproviderrelation___deleted=False,
                dataproviderrelation__data__in=self.data,
            )
            .distinct()
            .order_by("name")
        )
        data = [
            [
                Paragraph("REQUIREMENT UID", self.headerstyle_table1),
                Paragraph("REQUIREMENT", self.headerstyle_table1),
                Paragraph("NOTE", self.headerstyle_table1),
                Paragraph("DISSEMINATION", self.headerstyle_table1),
                Paragraph("QUALITY CONTROL", self.headerstyle_table1),
                Paragraph("GROUP", self.headerstyle_table1),
                Paragraph("UNCERTAINTY (%)", self.headerstyle_table1),
                Paragraph("UPDATE FREQUENCY", self.headerstyle_table1),
                Paragraph("TIMELINESS", self.headerstyle_table1),
                Paragraph("SCALE", self.headerstyle_table1),
                Paragraph("HORIZONTAL RESOLUTION", self.headerstyle_table1),
            ]
        ]

        data.extend(
            [
                [
                    Paragraph(str(x.id), self.rowstyle_table1),
                    Paragraph(x.name, self.rowstyle_table1),
                    Paragraph(x.note, self.rowstyle_table1),
                    Paragraph(x.dissemination.name, self.rowstyle_table1),
                    Paragraph(x.quality_control_procedure.name, self.rowstyle_table1),
                    Paragraph(x.group.name, self.rowstyle_table1),
                    Paragraph(x.uncertainty.breakthrough, self.rowstyle_table1),
                    Paragraph(x.update_frequency.breakthrough, self.rowstyle_table1),
                    Paragraph(x.timeliness.breakthrough, self.rowstyle_table1),
                    Paragraph(x.scale.breakthrough, self.rowstyle_table1),
                    Paragraph(
                        x.horizontal_resolution.breakthrough, self.rowstyle_table1
                    ),
                ]
                for x in self.requirements
            ]
        )

        t = Table(
            data, colWidths=[60, 60, 200, 60, 60, 50, 60, 60, 60, 60, 60], repeatRows=1
        )
        t.setStyle(self.LIST_STYLE)
        return t

    def generate_table_2_pdf(self):
        data = [
            [
                Paragraph("PRODUCT", self.table_headerstyle),
                Paragraph("DESCRIPTION", self.table_headerstyle),
            ]
        ]

        data.extend(
            [
                [
                    Paragraph(x.name, self.rowstyle),
                    Paragraph(strip_tags(x.description), self.rowstyle),
                ]
                for x in self.products
            ]
        )

        t = Table(data, colWidths=[80, 700], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
        return t

    def generate_table_3_pdf(self):
        data = [
            [
                Paragraph("PRODUCT", self.table_headerstyle),
                Paragraph("REQUIREMENT", self.table_headerstyle),
                Paragraph("REQUIREMENT UID", self.table_headerstyle),
            ]
        ]

        table_data = []
        count_for_merge = 1
        count_after_merge = 1
        span_for_merging = []
        for product in self.products:
            product_name = product.name
            product_requirements = product.product_requirements.filter(
                _deleted=False, requirement_id__in=self.requirements
            ).order_by("requirement__name")
            for idx, productrequirement in enumerate(product_requirements):
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph(productrequirement.requirement.name, self.rowstyle),
                        Paragraph(
                            str(productrequirement.requirement.id), self.rowstyle
                        ),
                    ]
                )
                if idx >= 1:
                    count_after_merge += 1
                product_name = ""

            if not product_requirements:
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                    ]
                )
            count_after_merge += 1
            count_for_merge = count_after_merge
            span_for_merging.append(
                ("LINEABOVE", (0, count_for_merge), (0, count_after_merge), 0.25, black)
            )
        data.extend(table_data)
        style = []
        style.extend(span_for_merging)
        style.extend(
            [
                ("INNERGRID", (1, 0), (-1, -1), 0.25, black),
                ("LINEBELOW", (0, 0), (1, 0), 0.25, black),
                ("LINEAFTER", (0, 0), (-1, -1), 0.25, black),
                ("LINEBEFORE", (0, 0), (-1, -1), 0.25, black),
                ("BOX", (0, 0), (-1, -1), 0.75, black),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
        t = Table(data, colWidths=[200, 400, 100], repeatRows=1)
        t.setStyle(TableStyle(style))
        return t

    def generate_table_4_pdf(self):
        data = [
            [
                Paragraph("REQUIREMENT", self.table_headerstyle),
                Paragraph("REQUIREMENT UID", self.table_headerstyle),
                Paragraph("DATA", self.table_headerstyle),
                Paragraph("DATA PROVIDER", self.table_headerstyle),
                Paragraph("DATA PROVIDER TYPE", self.table_headerstyle),
            ]
        ]

        table_data = []
        count_for_merge = 1
        count_after_merge = 1
        span_for_merging = []
        for requirement in self.requirements:
            requirement_name = requirement.name
            requirement_id = requirement.id
            data_objects = (
                Data.objects.filter(
                    requirements__in=[requirement],
                    datarequirement___deleted=False,
                )
                .filter(id__in=self.data)
                .distinct()
                .order_by("name")
            )
            for idx, data_object in enumerate(data_objects):
                data_name = data_object.name
                for idx_2, data_provider_relation in enumerate(
                    data_object.dataproviderrelation_set.filter(
                        _deleted=False
                    ).order_by("provider__name")
                ):
                    data_provider = data_provider_relation.provider
                    table_data.append(
                        [
                            Paragraph(requirement_name, self.rowstyle),
                            Paragraph(str(requirement_id), self.rowstyle),
                            Paragraph(data_name, self.rowstyle),
                            Paragraph(data_provider.name, self.rowstyle),
                            Paragraph(
                                getattr(
                                    getattr(
                                        data_provider.details.first(),
                                        "provider_type",
                                        "",
                                    ),
                                    "name",
                                    "",
                                ),
                                self.rowstyle,
                            ),
                        ]
                    )
                    count_after_merge += 1
                    requirement_name = ""
                    data_name = ""
                    requirement_id = ""
                if not data_object.dataproviderrelation_set.all():
                    table_data.append(
                        [
                            Paragraph(requirement_name, self.rowstyle),
                            Paragraph(str(requirement_id), self.rowstyle),
                            Paragraph(data_name, self.rowstyle),
                            Paragraph("", self.rowstyle),
                            Paragraph("", self.rowstyle),
                        ]
                    )
                    data_name = ""
                    requirement_name = ""
                    requirement_id = ""
                    count_after_merge += 1
                count_for_merge = count_after_merge
                span_for_merging.append(
                    (
                        "LINEABOVE",
                        (2, count_for_merge),
                        (2, count_after_merge),
                        0.25,
                        black,
                    )
                )

            if not data_objects:
                table_data.append(
                    [
                        Paragraph(requirement_name, self.rowstyle),
                        Paragraph(str(requirement_id), self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                    ]
                )
                requirement_name = ""
                requirement_id = ""
                count_after_merge += 1
                span_for_merging.append(
                    (
                        "LINEABOVE",
                        (2, count_for_merge),
                        (2, count_after_merge),
                        0.20,
                        black,
                    )
                )

            span_for_merging.append(
                ("LINEABOVE", (0, count_for_merge), (0, count_after_merge), 0.20, black)
            )
            span_for_merging.append(
                ("LINEABOVE", (1, count_for_merge), (1, count_after_merge), 0.20, black)
            )

        data.extend(table_data)
        style = []
        style.extend(span_for_merging)
        style.extend(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("BOX", (0, 0), (-1, -1), 0.75, black),
                ("INNERGRID", (3, 0), (-1, -1), 0.25, black),
                ("LINEBELOW", (0, 0), (2, 0), 0.25, black),
                ("LINEAFTER", (0, 0), (-1, -1), 0.25, black),
                ("LINEBEFORE", (0, 0), (-1, -1), 0.20, black),
            ]
        )
        t = Table(data, colWidths=[150, 125, 150, 150, 90], repeatRows=1)
        t.setStyle(TableStyle(style))
        return t

    def generate_table_5_pdf(self):
        data = [
            [
                Paragraph("PRODUCT", self.table_headerstyle),
                Paragraph("REQUIREMENT", self.table_headerstyle),
                Paragraph("REQUIREMENT UID", self.table_headerstyle),
                Paragraph("BARRIER", self.table_headerstyle),
                Paragraph("RELEVANCE", self.table_headerstyle),
                Paragraph("CRITICALITY", self.table_headerstyle),
            ]
        ]

        count_for_merge = 1
        count_after_merge = 1
        span_for_merging = []
        table_data = []
        for product in self.products:
            product_name = product.name
            product_requirements = product.product_requirements.filter(
                _deleted=False
            ).order_by("requirement__name")
            for idx, product_requirement in enumerate(product_requirements):
                requirement = product_requirement.requirement
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph(requirement.name, self.rowstyle),
                        Paragraph(str(requirement.id), self.rowstyle),
                        Paragraph(
                            "\n".join(
                                [x.name for x in product_requirement.barriers.all()]
                            ),
                            self.rowstyle,
                        ),
                        Paragraph(product_requirement.relevance.name, self.rowstyle),
                        Paragraph(product_requirement.criticality.name, self.rowstyle),
                    ]
                )
                if idx >= 1:
                    count_after_merge += 1
                product_name = ""
            if not product_requirements:
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                    ]
                )
            count_after_merge += 1
            count_for_merge = count_after_merge
            span_for_merging.append(
                ("LINEABOVE", (0, count_for_merge), (0, count_after_merge), 0.25, black)
            )

        data.extend(table_data)
        style = []
        style.extend(span_for_merging)
        style.extend(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("BOX", (0, 0), (-1, -1), 0.75, black),
                ("INNERGRID", (1, 0), (-1, -1), 0.25, black),
                ("LINEBELOW", (0, 0), (1, 0), 0.25, black),
                ("LINEAFTER", (0, 0), (-1, -1), 0.25, black),
                ("LINEBEFORE", (0, 0), (-1, -1), 0.25, black),
            ]
        )
        t = Table(data, colWidths=[150, 150, 100, 100, 100, 100], repeatRows=1)
        t.setStyle(TableStyle(style))
        return t

    def generate_table_6_pdf(self):
        data = [
            [
                Paragraph("PRODUCT", self.table_headerstyle),
                Paragraph("DATA", self.table_headerstyle),
                Paragraph("REQUIREMENT", self.table_headerstyle),
                Paragraph("REQUIREMENT UID", self.table_headerstyle),
                Paragraph(
                    "LEVEL OF COMPLIANCE DATA vs REQUIREMENT", self.table_headerstyle
                ),
                Paragraph("DATA LINK NOTE", self.table_headerstyle),
            ]
        ]

        count_for_merge = 1
        count_after_merge = 1
        span_for_merging = []
        table_data = []
        for product in self.products:
            product_name = product.name
            requirements = [
                x.requirement
                for x in product.product_requirements.filter(
                    _deleted=False,
                )
            ]
            data_objects = (
                Data.objects.filter(
                    datarequirement__requirement__in=requirements,
                    datarequirement___deleted=False,
                )
                .distinct()
                .order_by("name")
            )
            for idx, data_object in enumerate(data_objects):
                data_name = data_object.name
                data_requirements = data_object.datarequirement_set.filter(
                    requirement_id__in=self.requirements, _deleted=False
                ).order_by("requirement__name")
                for idx_2, data_requirement in enumerate(data_requirements):
                    table_data.append(
                        [
                            Paragraph(product_name, self.rowstyle),
                            Paragraph(data_name, self.rowstyle),
                            Paragraph(data_requirement.requirement.name, self.rowstyle),
                            Paragraph(
                                str(data_requirement.requirement.id), self.rowstyle
                            ),
                            Paragraph(
                                data_requirement.level_of_compliance.name, self.rowstyle
                            ),
                            Paragraph(data_requirement.note, self.rowstyle),
                        ]
                    )
                    if idx_2 >= 1:
                        count_after_merge += 1
                    product_name = ""
                    data_name = ""
                if not data_requirements:
                    table_data.append(
                        [
                            Paragraph(product_name, self.rowstyle),
                            Paragraph(data_name, self.rowstyle),
                            Paragraph("", self.rowstyle),
                            Paragraph("", self.rowstyle),
                            Paragraph("", self.rowstyle),
                        ]
                    )
                    product_name = ""
                    data_name = ""
                count_after_merge += 1
                count_for_merge = count_after_merge
                span_for_merging.append(
                    (
                        "LINEABOVE",
                        (1, count_for_merge),
                        (1, count_after_merge),
                        0.25,
                        black,
                    )
                )

            if not data_objects:
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                    ]
                )
                product_name = ""
                data_name = ""
                count_after_merge += 1
                span_for_merging.append(
                    (
                        "LINEABOVE",
                        (1, count_for_merge),
                        (1, count_after_merge),
                        0.25,
                        black,
                    )
                )

            span_for_merging.append(
                ("LINEABOVE", (0, count_for_merge), (0, count_after_merge), 0.25, black)
            )
        data.extend(table_data)
        style = []
        style.extend(span_for_merging)
        style.extend(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("BOX", (0, 0), (-1, -1), 0.75, black),
                ("INNERGRID", (2, 0), (-1, -1), 0.25, black),
                ("LINEBELOW", (0, 0), (1, 0), 0.25, black),
                ("LINEAFTER", (0, 0), (-1, -1), 0.25, black),
                ("LINEBEFORE", (0, 0), (-1, -1), 0.25, black),
            ]
        )
        t = Table(data, colWidths=[125, 125, 125, 125, 125], repeatRows=1)
        t.setStyle(TableStyle(style))
        return t

    def generate_table_7_pdf(self):
        data = [
            [
                Paragraph("DATA", self.table_headerstyle),
                Paragraph("DATA TYPE", self.table_headerstyle),
                Paragraph("DATA FORMAT", self.table_headerstyle),
                Paragraph("DATA UPDATE FREQUENCY", self.table_headerstyle),
                Paragraph("DATA AREA", self.table_headerstyle),
                Paragraph("DATA POLICY", self.table_headerstyle),
            ]
        ]

        self.data_objects = (
            Data.objects.filter(
                datarequirement__requirement__in=self.requirements,
                datarequirement___deleted=False,
            )
            .distinct()
            .order_by("name")
        )
        table_data = []
        for data_object in self.data_objects:
            table_data.append(
                [
                    Paragraph(data_object.name, self.rowstyle),
                    Paragraph(
                        getattr(data_object.data_type, "name", ""), self.rowstyle
                    ),
                    Paragraph(
                        getattr(data_object.data_format, "name", ""), self.rowstyle
                    ),
                    Paragraph(
                        getattr(data_object.update_frequency, "name", ""), self.rowstyle
                    ),
                    Paragraph(getattr(data_object.area, "name", ""), self.rowstyle),
                    Paragraph(
                        getattr(data_object.data_policy, "name", ""), self.rowstyle
                    ),
                ]
            )
        if not table_data:
            table_data.append(
                [
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                ]
            )
        data.extend(table_data)
        t = Table(data, colWidths=[125, 125, 125, 125, 125], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
        return t

    def generate_table_8_pdf(self):
        data = [
            [
                Paragraph("DATA", self.table_headerstyle),
                Paragraph("DATA PROVIDER", self.table_headerstyle),
                Paragraph("DATA PROVIDER TYPE", self.table_headerstyle),
                Paragraph("DATA PROVIDER ROLE", self.table_headerstyle),
                Paragraph("DATA QUALITY CONTROL", self.table_headerstyle),
                Paragraph("DATA DISSEMINATION", self.table_headerstyle),
                Paragraph("DATA TIMELINESS", self.table_headerstyle),
            ]
        ]

        count_for_merge = 1
        count_after_merge = 1
        span_for_merging = []
        table_data = []
        for data_object in self.data_objects:
            data_name = data_object.name
            data_providers_relations = data_object.dataproviderrelation_set.filter(
                provider__in=self.data_providers, _deleted=False
            ).order_by("provider__name")
            for idx, dataprovider_relation in enumerate(data_providers_relations):
                dataprovider = dataprovider_relation.provider
                role = dataprovider_relation.get_role_display()
                table_data.append(
                    [
                        Paragraph(data_name, self.rowstyle),
                        Paragraph(dataprovider.name, self.rowstyle),
                        Paragraph(
                            getattr(
                                getattr(
                                    dataprovider.details.first(), "provider_type", ""
                                ),
                                "name",
                                "",
                            ),
                            self.rowstyle,
                        ),
                        Paragraph(
                            role,
                            self.rowstyle,
                        ),
                        Paragraph(
                            getattr(data_object.quality_control_procedure, "name", ""),
                            self.rowstyle,
                        ),
                        Paragraph(
                            getattr(data_object.dissemination, "name", ""),
                            self.rowstyle,
                        ),
                        Paragraph(
                            getattr(data_object.timeliness, "name", ""), self.rowstyle
                        ),
                    ]
                )
                if idx >= 1:
                    count_after_merge += 1
                data_name = ""

            if not data_providers_relations:
                table_data.append(
                    [
                        Paragraph(data_name, self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph(
                            "",
                            self.rowstyle,
                        ),
                        Paragraph("", self.rowstyle),
                        Paragraph(
                            getattr(data_object.quality_control_procedure, "name", ""),
                            self.rowstyle,
                        ),
                        Paragraph(
                            getattr(data_object.dissemination, "name", ""),
                            self.rowstyle,
                        ),
                        Paragraph(
                            getattr(data_object.timeliness, "name", ""), self.rowstyle
                        ),
                    ]
                )
            count_after_merge += 1
            count_for_merge = count_after_merge
            span_for_merging.append(
                ("LINEABOVE", (0, count_for_merge), (0, count_after_merge), 0.25, black)
            )
        if not table_data:
            table_data.append(
                [
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                    Paragraph("", self.rowstyle),
                ]
            )
        data.extend(table_data)
        style = []
        style.extend(span_for_merging)
        style.extend(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("BOX", (0, 0), (-1, -1), 0.75, black),
                ("INNERGRID", (1, 0), (-1, -1), 0.25, black),
                ("LINEBELOW", (0, 0), (1, 0), 0.25, black),
                ("LINEAFTER", (0, 0), (-1, -1), 0.25, black),
                ("LINEBEFORE", (0, 0), (-1, -1), 0.25, black),
            ]
        )
        t = Table(data, colWidths=[150, 150, 90, 90, 90, 120, 90], repeatRows=1)
        t.setStyle(TableStyle(style))
        return t

    def set_styles(self):
        styles = getSampleStyleSheet()
        self.header_style = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=16,
            textColor=Color(0, 0.6875, 0.3125, 1),
            leading=20,
            alignment=TA_CENTER,
        )

        self.sub_header_style = ParagraphStyle(
            name="SubHeaderStyle",
            fontName="Calibri-Bold",
            parent=styles["Normal"],
            fontSize=12,
            textColor=Color(0, 0.6875, 0.3125, 1),
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=60,
        )

        self.normal_style = ParagraphStyle(
            name="NormalStyle",
            fontName="Calibri",
            parent=styles["Normal"],
            fontSize=12,
            leftIndent=20,
            leading=20,
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

        self.rowstyle_table1 = ParagraphStyle(
            name="RowStyleTable1",
            fontName="Calibri",
            fontSize=6,
            leading=7,
            alignment=TA_LEFT,
        )

        self.headerstyle_table1 = ParagraphStyle(
            name="HeaderStyleTable1",
            fontName="Calibri-Bold",
            fontSize=6.5,
            leading=7,
            textColor=Color(0, 0.4375, 0.75, 1),
            alignment=TA_CENTER,
        )

        self.rowstyle = ParagraphStyle(
            name="RowStyle",
            fontName="Calibri",
            fontSize=10,
            leading=10,
            alignment=TA_LEFT,
        )

        self.rowstyle_introduction = ParagraphStyle(
            name="RowStyle",
            fontSize=12,
            spaceAfter=10,
            spaceBefore=0,
            leftIndent=100,
            rightIndent=100,
            alignment=TA_JUSTIFY,
        )

        self.rowstyle_bullet_introduction = ParagraphStyle(
            name="RowStyle",
            fontSize=12,
            spaceAfter=10,
            spaceBefore=0,
            bulletAnchor="start",
            bulletFontName="Symbol",
            bulletFontSize=10,
            bulletIndent=120,
            leftIndent=120,
            rightIndent=100,
            alignment=TA_JUSTIFY,
        )

        self.table_headerstyle = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            fontSize=12,
            leading=14,
            textColor=Color(0, 0.4375, 0.75, 1),
            alignment=TA_CENTER,
        )

        self.LIST_STYLE_LIST = [
            ("INNERGRID", (0, 0), (-1, -1), 0.25, black),
            ("BOX", (0, 0), (-1, -1), 0.75, black),
            ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        self.LIST_STYLE = TableStyle(self.LIST_STYLE_LIST)
        self.LIST_STYLE.wordWrap = "CFK"

    def generate_introduction_text(self):
        elements = [
            Paragraph(
                "The European Environment Agency (EEA) is entrusted with cross-cutting "
                "coordination of the Copernicus In Situ Component in order to provide "
                "Entrusted Entities with harmonized and, in particular, cross-cutting "
                "information about in situ data requirements and gaps.",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "The Copernicus In Situ Information System (CIS<sup>2</sup>) "
                "aims to provide a complete overview of requirements, gaps and data "
                "relevant to all Copernicus services.",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "The Standard Report should be used in combination with the "
                "State of Play Report that focuses on cross-cutting challenges "
                " and gaps and made available simultaneously.",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "CIS<sup>2</sup> links the in situ requirements specified by the "
                "Entrusted Entities to Copernicus products, in situ datasets, and "
                "data providers in order to provide a clear picture of <b> what "
                "data is already used </b> and <b>what would be needed to deliver "
                "improved and more reliable products</b> and monitoring services.",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "CIS<sup>2</sup> shows in situ data requirements and which datasets "
                "are used for each Copernicus Service product. For each product, "
                "datasets are characterised in terms of:",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet><b>Criticality:</b> the importance of the "
                "requirement for the supply of reliable products (Essential, "
                "Desirable, or Useful).",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet><b>Relevance:</b> the extent to which a "
                "dataset corresponds with the intended purpose (product generation, "
                "calibration and validation, support of exploitation).",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet><b>Compliance level:</b> how far the dataset "
                "meets the stated requirement (Fully, Partially, None).",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet><b>Barriers:</b> the main reasons why a given "
                "in situ requirement is not satisfied for the product concerned (e.g. "
                "accuracy, availability, timeliness, update frequency, coverage).",
                self.rowstyle_bullet_introduction,
            ),
            PageBreak(),
            Paragraph(
                "As well as demonstrating in general terms the crucial importance "
                "of in situ data for the operation of the Copernicus Services, the "
                "information in the database helps to identify, for example:",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>Which datasets are in use and data providers",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>The priority requirements for in situ data",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>Gaps in data provision",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>Barriers to the effective use of the data",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>Requirements and issues which affect "
                "more than one service component or dataset",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<bullet>&bull;</bullet>Priority areas for action to improve provision",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "The database therefore provides an essential building block for "
                "the development of new actions to improve and promote sustainable "
                "data provision and hence effective user-driven services.",
                self.rowstyle_introduction,
            ),
            Paragraph(
                "This Report sets out in a systematic way the information contained "
                "in the database relating to the {} Service component."
                "The tables in the following pages show:".format(
                    ", ".join([elem.name for elem in self.components])
                ),
                self.rowstyle_introduction,
            ),
            Paragraph(
                "<link href='#requirements_detail' color='blue'>1. Requirements and "
                "the standards that need to be met (scale, timeliness, etc.)</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#products_descriptions' color='blue'>2. A simple list "
                "of products, not related to requirements</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#products_requirements' color='blue'>3. Data "
                "requirements by product</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#datasets_requirement_providers' color='blue'>4. "
                "Datasets and their providers relevant to each requirement</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#details_requirements_products' color='blue'>5. "
                "For each product, the attributes of each of these datasets relevant "
                "to their use (criticality, relevance, and barriers)</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#compliance_datasets_requirements' color='blue'>6. For "
                "each product, how far the datasets available comply with the "
                "requirements identified, and what issues about compliance "
                "are identified</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#datasets' color='blue'>7. The key characteristics "
                "of each dataset identified</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "<link href='#datasets_providers' color='blue'>8. The provider "
                "of each dataset, and arrangements for dissemination, updating "
                "and quality control.</link>",
                self.rowstyle_bullet_introduction,
            ),
            Paragraph(
                "The CIS<sup>2</sup> database continues to evolve, and updates "
                "of this and the other CIS<sup>2</sup> Standard Reports will be "
                "made available periodically. They will inform discussion between "
                "the EEA and the Services, and with wider stakeholders such as "
                "regulators and data owners, contributing to identifying actions "
                "necessary to provide improved user-driven services. It is therefore "
                "very important that they be carefully studied so that a shared "
                "narrative can be developed.",
                self.rowstyle_introduction,
            ),
        ]
        return elements

    def generate_pdf_file(self, menu_pdf):
        self.set_styles()
        elements = [
            Paragraph(
                "Copernicus In Situ Component Information System "
                "- managed by the European Environment Agency",
                self.header_style,
            ),
            Paragraph(
                "Standard Report for {} Component".format(
                    ", ".join([elem.name for elem in self.components])
                ),
                self.header_style,
            ),
            Paragraph(
                "Produced on {}".format(datetime.datetime.now().strftime("%d %B %Y")),
                self.sub_header_style,
            ),
        ]
        elements.extend(self.generate_introduction_text())

        elements.extend(
            [
                PageBreak(),
                Paragraph(
                    "<a name='requirements_detail'/>REQUIREMENTS AND THEIR DETAILS",
                    self.table_header_style,
                ),
            ]
        )
        table1 = self.generate_table_1_pdf()
        elements.append(table1)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='products_descriptions'/>PRODUCTS AND THEIR DESCRIPTIONS",
                self.table_header_style,
            )
        )
        table2 = self.generate_table_2_pdf()
        elements.append(table2)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='products_requirements'/>PRODUCTS AND ASSOCIATED REQUIREMENTS",
                self.table_header_style,
            )
        )
        table3 = self.generate_table_3_pdf()
        elements.append(table3)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='datasets_requirement_providers'/>"
                "DATASETS AND RELATED DATA PROVIDERS PER REQUIREMENT",
                self.table_header_style,
            )
        )
        table4 = self.generate_table_4_pdf()
        elements.append(table4)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='details_requirements_products'/>"
                "MAIN DETAILS BETWEEN REQUIREMENTS AND PRODUCTS",
                self.table_header_style,
            )
        )
        table5 = self.generate_table_5_pdf()
        elements.append(table5)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='compliance_datasets_requirements'/>"
                "LEVEL OF COMPLIANCE BETWEEN DATASETS AND REQUIREMENTS",
                self.table_header_style,
            )
        )
        table6 = self.generate_table_6_pdf()
        elements.append(table6)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='datasets'/>DATASETS MAIN DETAILS", self.table_header_style
            )
        )
        table7 = self.generate_table_7_pdf()
        elements.append(table7)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "<a name='datasets_providers'/>DATASETS AND RELATED DATA PROVIDERS",
                self.table_header_style,
            )
        )
        table8 = self.generate_table_8_pdf()
        elements.append(table8)
        menu_pdf.build(elements)


class CountryReportExcelMixin:
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
        worksheet.merge_range("H1:J1", "Additional information", self.merge_format_dark)
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
                    dataproviderrelation__provider=dp, dataproviderrelation___deleted=fl
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
            "Produced on {}".format(datetime.datetime.now().strftime("%d %B %Y")),
            self.merge_format_introduction,
        )
        worksheet.merge_range("A5:D5", "", self.format_rows_introduction)
        bold = workbook.add_format({"bold": True})
        worksheet.set_row(5, 560)
        superscript = workbook.add_format({"font_script": 1})
        worksheet.write_rich_string(
            "A5",
            "The European Environment Agency (EEA) is entrusted with cross-cutting ",
            "coordination of the Copernicus’ access to in situ data, in order to provide \n ",
            "Entrusted Entities with harmonized and, in particular, cross-cutting ",
            "information about in situ data requirements and gaps. \n\n",
            "The Copernicus In Situ Information System CIS",
            superscript,
            "2 ",
            "(https://cis2.eea.europa.eu) aims to provide a complete overview of requirements, ",
            "gaps and data relevant to all Copernicus services. CIS² links the in situ requirements\n ",
            "specified by the Entrusted Entities to Copernicus products, in situ datasets, ",
            "and data providers in order to provide a clear picture of what data is already used\n ",
            "and what would be needed to deliver improved and more reliable products and monitoring services. \n\n ",
            "The Country Report provides an overview of national organisations which are providing ",
            "in situ observations data to support Copernicus products. In-Situ observations are\n ",
            "non-satellite measurements of physical parameters. Observations are either direct ",
            "measurements of properties like temperature, wind, ozone, air quality, vegetation\n ",
            "properties, ocean salinity or ground based remote sensing data like soundings of ",
            "the atmospheric composition. Observations are provided to Copernicus either as\n ",
            "individual datasets or aggregated into gridded 2- or 3- dimensional analysis fields. \n\n",
            "Organisations are listed across two categories \n\n",
            "    • ",
            bold,
            "Data Providers ",
            "(listed in The report is based fully on the CIS2 database content. ",
            "The CIS² database also contains similar information regarding geospatial data, but these",
            "are not included in this country report.): these are organisations based in the Country",
            "which provide in situ observations data to support Copernicus products\n\n",
            "    • ",
            bold,
            "Data Provider Networks ",
            "(listed in Table 2): these are international networks with ",
            "members based in the Country, which provide in situ observations data to support Copernicus products.\n\n",
            "The report is based fully on the CIS2 database content. The CIS",
            superscript,
            "2",
            "database also contains similar information regarding geospatial data, but these are not",
            "included in this country report. ",
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
        worksheet.merge_range("I1:K1", "Additional information", self.merge_format_dark)
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
                    dataproviderrelation__provider=dp, dataproviderrelation___deleted=fl
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

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("Introduction")
        self.generate_header_sheet(workbook, worksheet)
        worksheet = workbook.add_worksheet("Data provider organisations")
        self.generate_table(workbook, worksheet, self.dataproviders)

        worksheet = workbook.add_worksheet("Data provider networks")
        self.generate_table_networks(workbook, worksheet, self.dataproviders_networks)


class VerticalParagraph(Paragraph):
    """Paragraph that is printed vertically"""

    def __init__(self, args, **kwargs):
        super().__init__(args, **kwargs)
        self.horizontal_position = -self.style.leading

    def draw(self):
        """Draw text"""
        canvas = self.canv
        canvas.rotate(90)
        canvas.translate(1, self.horizontal_position)
        super().draw()

    def wrap(self, available_width, _):
        """Wrap text in table"""
        string_width = self.canv.stringWidth(
            self.getPlainText(), self.style.fontName, self.style.fontSize
        )
        self.horizontal_position = -(available_width + self.style.leading) / 2
        height, _ = super().wrap(
            availWidth=1 + string_width, availHeight=available_width
        )
        return self.style.leading, height


class CountryReportPDFMixin:
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
                "Copernicus In Situ Component Information System - managed by the European Environment Agency",
                self.introduction_text_header,
            )
        )
        data.append(
            Paragraph(
                f"Country Report for {country_name} - Observations",
                self.introduction_text_header,
            )
        )
        current_date = datetime.datetime.now().strftime("%d %B %Y")
        data.append(
            Paragraph(f"Produced on {current_date}", self.introduction_text_subheader)
        )
        data.append(
            Paragraph(
                "The European Environment Agency (EEA) is entrusted with cross-cutting coordination of the Copernicus’ access to in situ data, in order to provide Entrusted Entities with harmonized and, in particular, cross-cutting information about in situ data requirements and gaps.",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "The Copernicus In Situ Information System CIS² (<link href='https://cis2.eea.europa.eu' color='blue'>https://cis2.eea.europa.eu</link>) aims to provide a complete overview of requirements, gaps and data relevant to all Copernicus services. CIS² links the in situ requirements specified by the Entrusted Entities to Copernicus products, in situ datasets, and data providers in order to provide a clear picture of what data is already used and what would be needed to deliver improved and more reliable products and monitoring services.",
                self.introduction_text_paragraph,
            )
        )
        data.append(
            Paragraph(
                "The Country Report provides an overview of national organisations which are providing in situ observations data to support Copernicus products. In-Situ observations are non-satellite measurements of physical parameters. Observations are either direct measurements of properties like temperature, wind, ozone, air quality, vegetation properties, ocean salinity or ground based remote sensing data like soundings of the atmospheric composition. Observations are provided to Copernicus either as individual datasets or aggregated into gridded 2- or 3- dimensional analysis fields.",
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
                "- <strong>Data Providers</strong> (listed in The report is based fully on the CIS2 database content. The CIS² database also contains similar information regarding geospatial data, but these are not included in this country report.): these are organisations based in the Country which provide in situ observations data to support Copernicus products",
                self.introduction_text_paragraph_bullet_list,
            )
        )
        data.append(
            Paragraph(
                " - <strong>Data Provider Networks</strong> (listed in Table 2): these are international networks with members based in the Country, which provide in situ observations data to support Copernicus products.",
                self.introduction_text_paragraph_bullet_list,
            )
        )

        data.append(
            Paragraph(
                "The report is based fully on the CIS² database content. The CIS² database also contains similar information regarding geospatial data, but these are not included in this country report.",
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
                    dataproviderrelation__provider=dp, dataproviderrelation___deleted=fl
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
        t = Table(data, colWidths=[200, 30, 30, 30, 30, 30, 30, 150, 200], repeatRows=1)
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
                    dataproviderrelation__provider=dp, dataproviderrelation___deleted=fl
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
