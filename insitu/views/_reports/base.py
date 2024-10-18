from datetime import datetime
from io import BytesIO
from xlsxwriter import Workbook

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate

from django.http import HttpResponse


class BaseReportMixin:

    def generate_filename(self, base, extension):
        now = datetime.now()
        return f"{base}_{now:%d%m%Y_%H%M}.{extension}"


class BaseExcelMixin(BaseReportMixin):

    def set_formats(self, workbook):
        raise NotImplementedError

    def generate_worksheets(self, workbook, data):
        raise NotImplementedError

    def generate_excel_file(self, workbook, data=None, formats=None):
        self.set_formats(workbook)
        self.generate_worksheets(workbook, data)

    def generate_excel(self, filename, data=None):
        output = BytesIO()
        workbook = Workbook(output)
        self.generate_excel_file(workbook, data)
        workbook.close()
        output.seek(0)
        cont_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(
            output,
            content_type=cont_type,
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class BasePDFMixin(BaseReportMixin):

    def set_styles(self):
        raise NotImplementedError

    def generate_pdf(self, filename):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=%s" % filename
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
