import datetime
import string
import xlsxwriter

from insitu.utils import get_object

from io import BytesIO
from Levenshtein import distance
from openpyxl import load_workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate
from wkhtmltopdf.views import PDFTemplateResponse

from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Subquery, OuterRef
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views import View

from explorer.app_settings import UNSAFE_RENDERING
from explorer.exporters import get_exporter_class
from explorer.models import Query
from explorer.views import DownloadQueryView
from explorer.views.export import _export
from explorer.utils import extract_params

from insitu.forms import (
    CountryReportForm,
    DataNetworkReportForm,
    StandardReportForm,
    DataProviderDuplicatesReportForm,
    UserActionsForm,
)
from insitu.models import (
    Component,
    CopernicusService,
    Product,
    DataProvider,
    DataProviderDetails,
    LoggedAction,
)
from insitu.views.data_provider_network_report_mixin import (
    DataProviderNetworkReportExcelMixin,
)
from insitu.views.protected.permissions import IsAuthenticated
from insitu.views.reportsmixins import (
    ReportExcelMixin,
    PDFExcelMixin,
    CountryReportExcelMixin,
    CountryReportPDFMixin,
)
from insitu.views.protected.views import ProtectedTemplateView, ProtectedView
from picklists.models import Country


def as_text(value):
    if value is None:
        return ""
    return str(value)


class ReportsListView(ProtectedTemplateView):
    template_name = "reports/list.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super(ReportsListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["queries"] = (
                Query.objects.exclude(id__in=[11, 12, 13, 14])
                .order_by("id")
                .values("id", "title", "description")
            )
        else:
            context["queries"] = (
                Query.objects.exclude(id__in=[1, 8, 11, 12, 17])
                .order_by("id")
                .values("id", "title", "description")
            )
        return context


class ReportsDetailView(ProtectedTemplateView):
    template_name = "reports/detail.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if kwargs["query_id"] in ["1", "8", "11", "12", "17"]:
                return HttpResponse(
                    "You don't have permission to access this page", status=403
                )
        try:
            pk = int(kwargs["query_id"])
            self.report = get_object_or_404(Query, pk=pk)
            return super(ReportsDetailView, self).get(request, *args, **kwargs)
        except ValueError:
            return HttpResponse("Invalid query id", status=400)

    def get_filename(self, title):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = "".join(c for c in title if c in valid_chars)
        filename = filename.replace(" ", "_")
        return filename

    def get_context_data(self, **kwargs):
        context = super(ReportsDetailView, self).get_context_data(**kwargs)
        self.report.execute_query_only()
        context["query"] = {
            "id": self.report.id,
            "title": self.report.title,
            "description": self.report.description,
            "params": extract_params(self.report.sql),
        }
        filename = self.get_filename(
            self.report.title
        ) + datetime.datetime.now().strftime("%Y%m%d")
        context.update(
            {
                "html_filename": filename + ".html",
                "pdf_filename": filename + ".pdf",
                "excel_filename": filename + ".xlsx",
                "no_jquery": True,
                "unsafe_rendering": UNSAFE_RENDERING,
            }
        )
        return context


class ReportDataJsonView(ProtectedView):
    def get(self, request, *args, **kwargs):
        self.report = get_object_or_404(Query, pk=kwargs["query_id"])
        res = self.report.execute_query_only()
        data = []
        for row in res.data:
            column_count = 0
            row_data = {}
            for column in res.headers:
                row_data[column.title] = str(row[column_count])
                column_count = column_count + 1
            data.append(row_data)

        return JsonResponse(data, safe=False)


class SnapshotView(ProtectedTemplateView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse()
        date = datetime.datetime.now().strftime("%Y%m%d")
        response["Content-Disposition"] = (
            "attachment; filename=insitu_{0}.sql.gz".format(date)
        )
        response["X-Accel-Redirect"] = "/static/protected/database.sql.gz"
        return response


class DownloadReportsView(DownloadQueryView):
    def get(self, request, query_id, *args, **kwargs):
        query = get_object_or_404(Query, pk=query_id)
        format = request.GET.get("format", "csv")
        exporter_class = get_exporter_class(format)
        file_extension = exporter_class.file_extension
        date = "_" + datetime.datetime.now().strftime("%Y%m%d")
        response = _export(request, query)
        response["Content-Disposition"] = (date + file_extension).join(
            response["Content-Disposition"].split(file_extension)
        )
        if file_extension == ".xlsx":
            wb = load_workbook(filename=BytesIO(response.content))
            ws = wb.active
            dims = {}
            for row in ws.iter_rows():
                for cell in row:
                    dims[cell.column] = max(
                        dims.get(cell.column, 0), len(as_text(cell.value))
                    )
            for col, value in dims.items():
                ws.column_dimensions[col].width = value
            wb.close()
            with BytesIO() as buffer:
                wb.save(buffer)
            response.content = buffer.getvalue()
        return response


class Pdf(View):
    def render(self, context, request):
        template = get_template("reports/reports_pdf.html")
        template_response = PDFTemplateResponse(
            request=request,
            template=template,
            filename="test.pdf",
            context=context,
            show_content_in_browser=False,
            cmd_options={
                "javascript-delay": 3000,
            },
        )
        template_response.render()
        content = template_response.rendered_content
        return HttpResponse(content, content_type="application/pdf")

    def post(self, request, *args, **kwargs):
        context = {
            "data": request.POST["data"],
            "title": request.POST.get("title", ""),
            "date": datetime.datetime.now().strftime("%Y %m %d"),
        }
        return self.render(context, request)


class ReportsStandardReportView(
    ProtectedTemplateView, ReportExcelMixin, PDFExcelMixin
):
    template_name = "reports/standard_report.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_filtered_services(self):
        # only take those services into consideration
        services = CopernicusService.objects.filter(
            acronym__in=["CEMS", "CLMS", "CSS", "CAMS", "C3S", "CMEMS", "CSC"]
        )
        return services

    def get_filtered_components(self, services):
        components = Component.objects.filter(service__in=services).exclude(
            acronym__in=["MWR", "SRAL", "OLCI", "SLSTR", "SLSTR/OLCI", "TROPOMI"]
        )
        return components

    def get_context_data(self, **kwargs):
        context = super(ReportsStandardReportView, self).get_context_data(**kwargs)
        context["services"] = self.get_filtered_services()
        context["components"] = self.get_filtered_components(context["services"])
        context["form"] = StandardReportForm()
        return context

    def generate_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_excel_file(workbook)
        workbook.close()
        output.seek(0)
        filename = self.generate_filename(".xlsx")
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

    def generate_filename(self, extension):
        services = "_".join([service.acronym for service in self.services])
        components = "_".join([component.acronym for component in self.components])
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = (
            "_".join(["Standard_Report", services, components, date]) + extension
        )
        return filename

    def generate_pdf(self):
        response = HttpResponse(content_type="application/pdf")
        pdf_name = self.generate_filename(".pdf")
        response["Content-Disposition"] = "attachment; filename=%s" % pdf_name

        buff = BytesIO()
        pdfmetrics.registerFont(
            TTFont(
                "Calibri",
                "/var/local/copernicus/insitu/static/fonts/CalibriRegular.ttf",
            )
        )
        pdfmetrics.registerFont(
            TTFont(
                "Calibri-Bold",
                "/var/local/copernicus/insitu/static/fonts/CalibriBold.ttf",
            )
        )
        pdfmetrics.registerFontFamily("Calibri", normal="Calibri", bold="CalibriBold")

        menu_pdf = SimpleDocTemplate(
            buff,
            rightMargin=10,
            pagesize=landscape(A4),
            leftMargin=10,
            topMargin=30,
            bottomMargin=10,
        )

        self.generate_pdf_file(menu_pdf)
        response.write(buff.getvalue())
        buff.close()
        return response

    def post(self, request, *args, **kwargs):
        services = self.request.POST.getlist("service")
        for service in services:
            try:
                int(service)
            except ValueError:
                raise Http404("Invalid service selected")
        components = self.request.POST.getlist("component")
        for component in components:
            try:
                int(component)
            except ValueError:
                raise Http404("Invalid component selected")
        self.services = CopernicusService.objects.filter(id__in=services)
        self.components = Component.objects.filter(id__in=components)
        self.products = Product.objects.filter(component_id__in=components).order_by(
            "name"
        )
        action = request.POST.get("action", "")
        if action == "Generate PDF":
            return self.generate_pdf()
        elif action == "Generate Excel":
            return self.generate_excel()
        else:
            return HttpResponse("Incorect value selected")


class CountryReportView(
    ProtectedTemplateView, CountryReportExcelMixin, CountryReportPDFMixin
):
    template_name = "reports/country_report.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super(CountryReportView, self).get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["country_form"] = CountryReportForm()
        context["data_networks_report_form"] = DataNetworkReportForm()
        return context

    def generate_filename(self, extension):
        country = Country.objects.get(code=self.country_code).name
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = "_".join([country, "Country_Report", date]) + extension
        return filename

    def post(self, request, *args, **kwargs):
        self.country_code = self.request.POST.getlist("country")[0]
        self.dataproviders = DataProvider.objects.filter(
            countries__code=self.country_code, is_network=False, _deleted=False
        ).order_by("name")
        self.dataproviders_networks = DataProvider.objects.filter(
            countries__code=self.country_code, is_network=True, _deleted=False
        ).order_by("name")
        action = request.POST.get("action", "")
        if action == "Generate PDF":
            return self.generate_pdf()
        elif action == "Generate Excel":
            return self.generate_excel()
        else:
            return HttpResponse("Incorect value selected")

    def generate_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_excel_file(workbook)
        workbook.close()
        output.seek(0)
        filename = self.generate_filename(".xlsx")
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

    def generate_pdf(self):
        response = HttpResponse(content_type="application/pdf")
        pdf_name = self.generate_filename(".pdf")
        response["Content-Disposition"] = "attachment; filename=%s" % pdf_name

        buff = BytesIO()
        pdfmetrics.registerFont(
            TTFont(
                "Calibri",
                "/var/local/copernicus/insitu/static/fonts/CalibriRegular.ttf",
            )
        )
        pdfmetrics.registerFont(
            TTFont(
                "Calibri-Bold",
                "/var/local/copernicus/insitu/static/fonts/CalibriBold.ttf",
            )
        )
        pdfmetrics.registerFontFamily("Calibri", normal="Calibri", bold="CalibriBold")

        menu_pdf = SimpleDocTemplate(
            buff,
            rightMargin=10,
            pagesize=landscape(A4),
            leftMargin=10,
            topMargin=30,
            bottomMargin=10,
        )

        self.generate_pdf_file(menu_pdf)
        response.write(buff.getvalue())
        buff.close()
        return response


class DataProviderDuplicatesReportView(
    ProtectedTemplateView, ReportExcelMixin, PDFExcelMixin
):
    template_name = "reports/data_provider_duplicates_report.html"
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super(DataProviderDuplicatesReportView, self).get_context_data(
            **kwargs
        )
        context["countries"] = Country.objects.all()
        context["form"] = DataProviderDuplicatesReportForm()
        return context

    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
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

    def post(self, request, *args, **kwargs):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_excel_file(workbook)
        workbook.close()
        output.seek(0)
        today = datetime.datetime.now().strftime("%d_%m_%Y")
        filename = f"CIS2_Potential_Provider_Duplicates_Report_{today}.xlsx"
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class DataProvidersNetwortReportView(
    ProtectedTemplateView, DataProviderNetworkReportExcelMixin
):
    template_name = "reports/country_report.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super(CountryReportView, self).get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["country_form"] = CountryReportForm()
        context["data_networks_report_form"] = DataNetworkReportForm()
        return context

    def generate_filename(self, extension):
        return "Data_networks_report" + extension
        country = Country.objects.get(code=self.country_code).name
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = "_".join([country, "Country_Report", date]) + extension
        return filename

    def post(self, request, *args, **kwargs):
        self.ACCEPTED_NETWORKS_IDS = [
            802,
            21,
            122,
            23,
            134,
            811,
            828,
            358,
            839,
            2,
            827,
            180,
            890,
            16,
            796,
            602,
            600,
        ]

        self.ACCEPTED_RESEARCH_INFRASTRUCTURES_IDS = [
            960,
            891,
            182,
            18,
            1083,
            10,
            889,
        ]
        country_codes = self.request.POST.getlist("countries")
        self.country_codes = None
        if "all" not in country_codes:
            self.country_codes = country_codes
        return self.generate_excel()

    def generate_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_excel_file(workbook)
        workbook.close()
        output.seek(0)
        filename = self.generate_filename(".xlsx")
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class UserActionsReportView(ProtectedTemplateView, ReportExcelMixin):
    template_name = "reports/user_actions_report.html"
    permission_classes = ()
    permission_denied_redirect = reverse_lazy("auth:login")

    def get_context_data(self, **kwargs):
        context = super(UserActionsReportView, self).get_context_data(**kwargs)
        context["form"] = UserActionsForm()
        return context

    def generate_excel_file(self, workbook, data):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet("")
        worksheet.set_column("A1:A1", 20)
        worksheet.set_column("B1:B1", 20)
        worksheet.set_column("C1:C1", 30)
        worksheet.set_column("D1:D1", 50)
        worksheet.set_column("E1:E1", 20)
        worksheet.set_column("F1:F1", 50)
        worksheet.set_column("G1:G1", 30)
        worksheet.set_column("H1:H1", 30)
        worksheet.set_column("I1:I1", 30)
        worksheet.set_column("J1:J1", 30)
        headers = [
            "LOGGED DATE",
            "USER",
            "ACTION",
            "TARGET TYPE",
            "TARGET ID",
            "TARGET NAME",
            "TARGET STATE",
            "TARGET LINK",
            "TARGET NOTE",
            "EXTRA",
        ]
        worksheet.write_row("A1", headers, self.format_cols_headers)
        users = [u.username for u in data["users"]]
        logged_actions = LoggedAction.objects.filter(
            logged_date__range=[data["start_date"], data["end_date"]]
        ).order_by("logged_date")
        if users:
            logged_actions = logged_actions.filter(user__in=users)
        index = 1
        for logged_action in logged_actions:
            target = None
            if logged_action.id_target:
                target = get_object(logged_action.id_target, logged_action.target_type)

            if target:
                target_name = target.name
                target_state = getattr(target, "state", "")
                if target_state and data["states"]:
                    if target_state not in data["states"]:
                        continue
                if logged_action.action != "deleted":
                    target_link = self.request.build_absolute_uri(
                        target.get_detail_link()
                    )
                else:
                    target_link = ""
            else:
                target = ""
                target_name = ""
                target_state = ""
                target_link = ""
            write_data = [
                logged_action.logged_date.strftime("%Y-%m-%d %H:%M:%S"),
                logged_action.user,
                logged_action.action,
                logged_action.target_type,
                logged_action.id_target,
                target_name,
                target_state,
                target_link,
                logged_action.target_note,
                logged_action.extra,
            ]
            worksheet.write_row(index, 0, write_data, self.format_rows)
            index += 1

    def post(self, request, *args, **kwargs):
        form = UserActionsForm(request.POST)
        if form.is_valid():
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            self.generate_excel_file(workbook, form.cleaned_data)
            workbook.close()
            output.seek(0)
            today = datetime.datetime.now().strftime("%d_%m_%Y")
            filename = f"CIS2_User_actions_{today}.xlsx"
            cont_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response = HttpResponse(
                output,
                content_type=cont_type,
            )
            response["Content-Disposition"] = "attachment; filename=%s" % filename
            return response
            return HttpResponse("Form is valid")
        return HttpResponse("Incorrect value selected")
