from insitu.models import CopernicusService, Component, Data, Product, Requirement
from django.utils.html import strip_tags

import datetime

from reportlab.platypus import (
    Paragraph,
    PageBreak,
    Table,
    TableStyle,
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, red, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT


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

    def generate_header_sheet(self, workbook, worksheet):
        worksheet.set_column("A1:D1", 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 20)
        worksheet.set_row(3, 20)
        worksheet.set_row(5, 20)
        worksheet.merge_range(
            "A1:D1",
            "Copernicus In Situ Component Information System - "
            "managed by the European Environment Agency",
            self.merge_format,
        )
        worksheet.merge_range(
            "A3:D3",
            "Standard Report for {}".format(
                ", ".join([elem.name for elem in self.components])
            ),
            self.merge_format,
        )

        worksheet.merge_range(
            "A4:D4",
            "Produced on {}".format(datetime.datetime.now().strftime("%d %B %Y")),
            self.merge_format,
        )
        worksheet.merge_range(
            "A6:D6",
            "The Standard Report consists of tables that "
            "include all the main statistical data.",
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
                products__in=self.products, product_requirements___deleted=False
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
            requirements = product.product_requirements.all()
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
            for datarequirement in requirement.datarequirement_set.all():
                provider_index = data_index
                for data_provider in datarequirement.data.providers.all():
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
                        [datarequirement.data.name, "", ""],
                        self.format_rows,
                    )
                    data_index = provider_index
                elif provider_index == data_index + 1:
                    worksheet.write_row(
                        data_index, 2, [datarequirement.data.name], self.format_rows
                    )
                else:
                    worksheet.merge_range(
                        data_index,
                        2,
                        provider_index - 1,
                        2,
                        datarequirement.data.name,
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
            product_merge_dimension = product.product_requirements.all().count()
            if product_merge_dimension >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + product_merge_dimension - 1,
                    0,
                    product.name,
                    self.format_rows,
                )
                for product_requirement in product.product_requirements.all():
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
                product_requirement = product.product_requirements.first()
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
            requirements = [x.requirement for x in product.product_requirements.all()]
            data = Data.objects.filter(
                requirements__in=requirements, datarequirement___deleted=False
            ).distinct()
            data_index = product_index
            for data_object in data:
                data_requirement_index = data_index
                for data_requirement in data_object.datarequirement_set.filter(
                    requirement_id__in=self.requirements
                ):
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
        self.data = (
            Data.objects.filter(
                requirements__in=self.requirements, datarequirement___deleted=False
            )
            .distinct()
            .order_by("name")
        )
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
        worksheet.set_column("C1:F1", 25)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            "A1:F1", "DATASETS AND RELATED DATA PROVIDERS", self.format_header
        )
        headers = [
            "DATA",
            "DATA PROVIDER",
            "DATA PROVIDER TYPE",
            "DATA QUALITY CONTROL",
            "DATA DISSEMINATION",
            "DATA TIMELINESS",
        ]
        worksheet.write_row("A2", headers, self.format_cols_headers)
        index = 2
        for data_object in self.data:
            provider_count = data_object.providers.all().count()
            if provider_count >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + provider_count - 1,
                    0,
                    data_object.name,
                    self.format_rows,
                )
                for dataprovider in data_object.providers.all():
                    row_data = [
                        dataprovider.name,
                        getattr(
                            getattr(dataprovider.details.first(), "provider_type", ""),
                            "name",
                            "",
                        ),
                        getattr(data_object.quality_control_procedure, "name", ""),
                        getattr(data_object.dissemination, "name", ""),
                        getattr(data_object.timeliness, "name", ""),
                    ]
                    worksheet.write_row(index, 1, row_data, self.format_rows)
                    index += 1
            elif provider_count == 1:
                dataprovider = data_object.providers.first()
                row_data = [
                    data_object.name,
                    dataprovider.name,
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
                    index, 0, [data_object.name, "", "", "", "", ""], self.format_rows
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
                products__in=self.products, product_requirements___deleted=False
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
                    Paragraph(x.horizontal_resolution.breakthrough, self.rowstyle_table1),
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
        for product in self.products:
            product_name = product.name
            product_requirements = product.product_requirements.all()
            for productrequirement in product_requirements:
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph(productrequirement.requirement.name, self.rowstyle),
                        Paragraph(
                            str(productrequirement.requirement.id), self.rowstyle
                        ),
                    ]
                )
                product_name = ""
            if not product_requirements:
                table_data.append(
                    [
                        Paragraph(product_name, self.rowstyle),
                        Paragraph("", self.rowstyle),
                        Paragraph("", self.rowstyle),
                    ]
                )

        data.extend(table_data)
        t = Table(data, colWidths=[200, 400, 100], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
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
        for requirement in self.requirements:
            requirement_name = requirement.name
            requirement_id = requirement.id
            for datarequirement in requirement.datarequirement_set.all():
                data_name = datarequirement.data.name
                for data_provider in datarequirement.data.providers.all():
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
                    requirement_name = ""
                    data_name = ""
                    requirement_id = ""
                if not datarequirement.data.providers.all():
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
            if not requirement.datarequirement_set.all():
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

        data.extend(table_data)

        t = Table(data, colWidths=[150, 125, 150, 150, 90], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
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

        table_data = []
        for product in self.products:
            product_name = product.name
            product_requirements = product.product_requirements.all()
            for product_requirement in product_requirements:
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

        data.extend(table_data)
        t = Table(data, colWidths=[150, 150, 100, 100, 100, 100], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
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

        table_data = []
        for product in self.products:
            product_name = product.name
            requirements = [x.requirement for x in product.product_requirements.all()]
            data_objects = Data.objects.filter(
                requirements__in=requirements, datarequirement___deleted=False
            ).distinct()
            for data_object in data_objects:
                data_name = data_object.name
                for data_requirement in data_object.datarequirement_set.filter(
                    requirement_id__in=self.requirements
                ):
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
                    product_name = ""
                    data_name = ""
                if not data_object.datarequirement_set.all():
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
            if not data:
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

        data.extend(table_data)
        t = Table(data, colWidths=[125, 125, 125, 125, 125], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
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
                requirements__in=self.requirements, datarequirement___deleted=False
            )
            .distinct()
            .order_by("name")
        )
        table_data = []
        for data_object in self.data_objects:
            data.append(
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
                Paragraph("DATA QUALITY CONTROL", self.table_headerstyle),
                Paragraph("DATA DISSEMINATION", self.table_headerstyle),
                Paragraph("DATA TIMELINESS", self.table_headerstyle),
            ]
        ]

        table_data = []
        for data_object in self.data_objects:
            data_name = data_object.name
            data_providers = data_object.providers.all()
            for dataprovider in data_providers:
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
                data_name = ""
            if not data_providers:
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

        data.extend(table_data)
        t = Table(data, colWidths=[150, 150, 90, 90, 120, 90], repeatRows=1)
        t.setStyle(self.LIST_STYLE)
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

        self.table_headerstyle = ParagraphStyle(
            name="HeaderStyle",
            fontName="Calibri-Bold",
            fontSize=12,
            leading=14,
            textColor=Color(0, 0.4375, 0.75, 1),
            alignment=TA_CENTER,
        )

        self.LIST_STYLE = TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, black),
                ("BOX", (0, 0), (-1, -1), 0.25, black),
                ("BACKGROUND", (0, 0), (-1, 0), Color(0.7617, 0.8359, 0.6054, 1)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
        self.LIST_STYLE.wordWrap = "CFK"

    def generate_pdf_file(self, menu_pdf):
        self.set_styles()
        elements = [
            Paragraph(
                "Copernicus In Situ Component Information System "
                "- managed by the European Environment Agency",
                self.header_style,
            ),
            Paragraph(
                "Standard Report for {}".format(
                    ", ".join([elem.name for elem in self.components])
                ),
                self.header_style,
            ),
            Paragraph(
                "Produced on {}".format(datetime.datetime.now().strftime("%d %B %Y")),
                self.sub_header_style,
            ),
            PageBreak(),
        ]
        elements.append(
            Paragraph("REQUIREMENTS AND THEIR DETAILS", self.table_header_style)
        )
        table1 = self.generate_table_1_pdf()
        elements.append(table1)
        elements.append(PageBreak())
        elements.append(
            Paragraph("PRODUCTS AND THEIR DESCRIPTIONS", self.table_header_style)
        )
        table2 = self.generate_table_2_pdf()
        elements.append(table2)
        elements.append(PageBreak())
        elements.append(
            Paragraph("PRODUCTS AND ASSOCIATED REQUIREMENTS", self.table_header_style)
        )
        table3 = self.generate_table_3_pdf()
        elements.append(table3)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "DATASETS AND RELATED DATA PROVIDERS PER REQUIREMENT",
                self.table_header_style,
            )
        )
        table4 = self.generate_table_4_pdf()
        elements.append(table4)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "MAIN DETAILS BETWEEN REQUIREMENTS AND PRODUCTS",
                self.table_header_style,
            )
        )
        table5 = self.generate_table_5_pdf()
        elements.append(table5)
        elements.append(PageBreak())
        elements.append(
            Paragraph(
                "LEVEL OF COMPLIANCE BETWEEN DATASETS AND REQUIREMENTS",
                self.table_header_style,
            )
        )
        table6 = self.generate_table_6_pdf()
        elements.append(table6)
        elements.append(PageBreak())
        elements.append(Paragraph("DATASETS MAIN DETAILS", self.table_header_style))
        table7 = self.generate_table_7_pdf()
        elements.append(table7)
        elements.append(PageBreak())
        elements.append(
            Paragraph("DATASETS AND RELATED DATA PROVIDERS", self.table_header_style)
        )
        table8 = self.generate_table_8_pdf()
        elements.append(table8)
        menu_pdf.build(elements)
