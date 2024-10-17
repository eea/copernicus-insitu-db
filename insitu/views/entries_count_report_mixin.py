from insitu.models import (
    DataProvider,
    Product,
    ProductRequirement,
    Requirement,
    Data,
    DataProviderRelation,
    DataRequirement,
)
from insitu.models import EntrustedEntity


class EntriesCountReportExcelMixin:
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

    def get_counts(self, component):
        products = Product.objects.filter(component=component)
        product_requirements = ProductRequirement.objects.filter(product__in=products)
        requirements = Requirement.objects.filter(
            id__in=product_requirements.values_list("requirement_id", flat=True)
        )
        data_requirements = DataRequirement.objects.filter(
            requirement__in=requirements
        )
        data = Data.objects.filter(
            id__in=data_requirements.values_list("data_id", flat=True)
        )
        data_provider_relations = DataProviderRelation.objects.filter(data__in=data)
        data_providers = DataProvider.objects.filter(
            id__in=data_provider_relations.values_list("provider_id", flat=True)
        )
        return requirements.count(), data.count(), data_providers.count()

    def generate_rows_for_root_entries(self, worksheet, entries, entries_index):
        for entry in entries:
            components = entry.components.all()
            component_index = entries_index
            for component in components:
                count_req, count_data, count_dp = self.get_counts(component)
                worksheet.write_row(
                    component_index,
                    1,
                    [
                        component.name,
                        count_req,
                        count_data,
                        count_dp,
                    ],
                    self.format_rows,
                )
                component_index += 1
            if component_index == entries_index:
                worksheet.write_row(
                    entries_index,
                    0,
                    [entry.name, "", "", "", ""],
                    self.format_rows,
                )
                entries_index += 1
            elif component_index == entries_index + 1:
                worksheet.write_row(entries_index, 0, [entry.name], self.format_rows)
                entries_index = component_index
            else:
                worksheet.merge_range(
                    entries_index,
                    0,
                    component_index - 1,
                    0,
                    entry.name,
                    self.format_rows,
                )
                entries_index = component_index

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column("A1:A1", 30)
        worksheet.set_column("B1:B1", 35)
        worksheet.set_column("C1:C1", 35)
        worksheet.set_column("D1:D1", 35)
        worksheet.set_column("E1:E1", 35)
        headers = [
            "Entrusted entity",
            "Component",
            "Number of Requirements",
            "Number of Datasets",
            "Number of Data Providers",
        ]
        worksheet.write_row("A1", headers, self.format_cols_headers)
        entrusted_entities = EntrustedEntity.objects.filter(
            id__in=self.entrusted_entities_ids
        )
        self.generate_rows_for_root_entries(worksheet, entrusted_entities, 1)

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("TABLE 1")
        self.generate_table_1(workbook, worksheet)
