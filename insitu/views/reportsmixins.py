from insitu.models import (
    Product, Requirement
)

class ReportExcelMixin:

    def set_formats(self, workbook):
        self.merge_format =  workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Calibri',
            'font_size': 14,
            'font_color': '#00B050',
        })

        self.format_header = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': 'Calibri',
            'font_size': 14,
            'font_color': 'red',
        })

        self.format_cols_headers = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Calibri',
            'font_size': 12,
            'font_color': '#0070C0',
            'bg_color': '#c3d69b',
            'border': 1,
        })

        self.format_rows = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_name': 'Calibri',
            'font_size': 12,
            'text_wrap': 1,
            'border': 1,
        })

    def generate_header_sheet(self, workbook, worksheet):
        worksheet.set_column('A1:D1', 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 20)
        worksheet.set_row(3, 20)
        worksheet.set_row(5, 20)
        worksheet.merge_range('A1:D1', 'Copernicus In Situ Component Information System - managed by the European Environment Agency', self.merge_format)
        worksheet.merge_range('A3:D3', 'Standard Report for Local Land Component', self.merge_format)
        worksheet.merge_range('A4:D4', 'Produced on 30th October 2020', self.merge_format)
        worksheet.merge_range('A6:D6', 'The Standard Report consists of tables that include  all the main  statistical data  . . . . .')

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column('A1:B1', 20)
        worksheet.set_column('B1:C1', 50)
        worksheet.set_column('D1:K1', 25)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 20)
        worksheet.merge_range('A1:K1', 'REQUIREMENTS AND THEIR DETAILS', self.format_header)
        headers = [
            'REQUIREMENT UID', 'REQUIREMENT', 'NOTE', 'DISSEMINATION',
            'QUALITY CONTROL', 'GROUP', 'UNCERTAINTY (%)', 'UPDATE FREQUENCY',
            'TIMELINESS', 'SCALE', 'HORIZONTAL RESOLUTION'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        requirements = Requirement.objects.all()
        index = 2
        for requirement in requirements:
            worksheet.set_row(index, 50)
            data = [
                requirement.id, requirement.name, requirement.note,
                requirement.dissemination.name, requirement.quality_control_procedure.name,
                requirement.group.name, 
                '{}\n{}\n{}\n'.format(requirement.uncertainty.threshold, requirement.uncertainty.breakthrough, requirement.uncertainty.goal),
                '{}\n{}\n{}\n'.format(requirement.update_frequency.threshold, requirement.update_frequency.breakthrough, requirement.update_frequency.goal),
                '{}\n{}\n{}\n'.format(requirement.timeliness.threshold, requirement.timeliness.breakthrough, requirement.timeliness.goal),
                '{}\n{}\n{}\n'.format(requirement.scale.threshold, requirement.scale.breakthrough, requirement.scale.goal),
                '{}\n{}\n{}\n'.format(requirement.horizontal_resolution.threshold, requirement.horizontal_resolution.breakthrough, requirement.horizontal_resolution.goal),
            ]
            worksheet.write_row(index, 0 , data, self.format_rows)
            index += 1

    def generate_table_2(self, workbook, worksheet):
        worksheet.set_column('A1:A1', 20)
        worksheet.set_column('B1:B1', 120)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range('A1:B1', 'PRODUCTS AND THEIR DESCRIPTIONS', self.format_header)
        headers = [
            'PRODUCT', 'DESCRIPTION'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        products = Product.objects.all()
        index = 2
        for product in products:
            data = [product.name, product.description]
            worksheet.write_row(index, 0 , data, self.format_rows)
            index += 1

    def generate_table_3(self, workbook, worksheet):
        worksheet.set_column('A1:B1', 20)
        worksheet.set_column('C1:C1', 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range('A1:B1', 'PRODUCTS AND ASSOCIATED REQUIREMENTS', self.format_header)
        headers = [
            'PRODUCT', 'REQUIREMENT', 'REQUIREMENT UID'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        products = Product.objects.all()
        index = 2
        for product in products:
            product_merge_dimension = product.requirements.all().count()
            if product_merge_dimension >= 2:
                worksheet.merge_range(index, 0, index + product_merge_dimension - 1, 0, product.name, self.format_rows)
                for requirement in product.requirements.all():
                    data = [requirement.name, requirement.id]
                    worksheet.write_row(index, 1 , data, self.format_rows)
                    index += 1
            elif product_merge_dimension == 1:
                worksheet.write_row(index, 0 , [product.name, product.requirements.first().name, product.requirements.first().id], self.format_rows)
                index += 1
            else:
                worksheet.write_row(index, 0 , [product.name, '', ''], self.format_rows)
                index += 1



    def generate_excel_file(self, workbook):
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet('INTRODUCTION')
        self.generate_header_sheet(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 1')
        self.generate_table_1(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 2')
        self.generate_table_2(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 3')
        self.generate_table_3(workbook, worksheet)
