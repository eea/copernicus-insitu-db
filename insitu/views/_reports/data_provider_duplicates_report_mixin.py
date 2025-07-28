from django.urls import reverse
from django.db.models import Subquery, OuterRef
from Levenshtein import distance

from insitu.models import DataProvider, DataProviderDetails
from insitu.views._reports.base import BaseExcelMixin

from picklists.models import Country


class DataProviderDuplicatesReportMixin(BaseExcelMixin):
    def set_formats(self, workbook):

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

    def check_providers_have_different_edmo(self, dp1, dp2):
        """
        Check if two data providers have the same EDMO code.
        Returns True only if both providers have an EDMO code and they are different.
        If one or both providers do not have an EDMO code, returns False.
        """
        if dp1.edmo and dp2.edmo:
            return dp1.edmo != dp2.edmo
        return False

    def generate_worksheets(self, workbook, data=None):
        worksheet = workbook.add_worksheet("")
        worksheet.set_column("A1:A1", 30)
        worksheet.set_column("B1:B1", 50)
        worksheet.set_column("C1:C1", 50)
        worksheet.set_column("D1:D1", 30)
        worksheet.set_column("E1:E1", 50)
        worksheet.set_column("F1:F1", 50)
        headers = [
            "PROVIDER LINK",
            "PROVIDER NAME",
            "PROVIDER WEBSITE",
            "DUPLICATE LINK",
            "DUPLICATE NAME",
            "DUPLICATE WEBSITE",
        ]
        if self.request.POST.get("country", None):
            country = Country.objects.get(code=self.request.POST["country"])
            title = f"Potential provider duplicates in {country.name}"
        else:
            country = None
            title = "Potential provider duplicates in all countries"
        worksheet.write_row("A1", [title], self.format_header)
        worksheet.write_row("A2", headers, self.format_cols_headers)

        data_providers = DataProvider.objects.all().annotate(
            website=Subquery(
                DataProviderDetails.objects.filter(
                    data_provider=OuterRef("pk"), _deleted=False
                ).values_list("website", flat=True)[:1]
            ),
        )

        if country:
            data_providers = data_providers.filter(countries__code=country.code)

        index = 2
        for dp in data_providers:
            dp_link = self.request.build_absolute_uri(
                reverse("provider:detail", kwargs={"pk": dp.id})
            )
            duplicates = [
                dp2
                for dp2 in data_providers
                if dp.id != dp2.id
                and not self.check_providers_have_different_edmo(dp, dp2)
                and (
                    distance(dp.name, dp2.name) <= 2
                    or (dp.website != "" and distance(dp.website, dp2.website) < 2)
                    or (dp.edmo and dp2.edmo and dp.edmo == dp2.edmo)
                )
            ]
            if len(duplicates) >= 2:
                worksheet.merge_range(
                    index,
                    0,
                    index + len(duplicates) - 1,
                    0,
                    dp_link,
                    self.format_rows,
                )
                worksheet.merge_range(
                    index,
                    1,
                    index + len(duplicates) - 1,
                    1,
                    dp.name,
                    self.format_rows,
                )
                worksheet.merge_range(
                    index,
                    2,
                    index + len(duplicates) - 1,
                    2,
                    dp.website,
                    self.format_rows,
                )

                for dp2 in duplicates:
                    dp2_link = self.request.build_absolute_uri(
                        reverse("provider:detail", kwargs={"pk": dp2.id})
                    )
                    data = [
                        dp2_link,
                        dp2.name,
                        dp2.website,
                    ]
                    worksheet.write_row(index, 3, data, self.format_rows)
                    index += 1
            elif len(duplicates) == 1:
                dp2 = duplicates[0]
                dp2_link = self.request.build_absolute_uri(
                    reverse("provider:detail", kwargs={"pk": dp2.id})
                )
                data = [
                    dp_link,
                    dp.name,
                    dp.website,
                    dp2_link,
                    dp2.name,
                    dp2.website,
                ]
                worksheet.write_row(index, 0, data, self.format_rows)
                index += 1
                continue
