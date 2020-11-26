from insitu.models import (
    CopernicusService, Component,
    Data, Product, Requirement
)


class ReportExcelMixin:

    def set_formats(self, workbook):
        self.merge_format = workbook.add_format({
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
        worksheet.merge_range(
            'A1:D1', 'Copernicus In Situ Component Information System - managed by the European Environment Agency', self.merge_format)
        worksheet.merge_range(
            'A3:D3', 'Standard Report for Local Land Component', self.merge_format)
        worksheet.merge_range(
            'A4:D4', 'Produced on 30th October 2020', self.merge_format)
        worksheet.merge_range(
            'A6:D6', 'The Standard Report consists of tables that include  all the main  statistical data  . . . . .')
        worksheet.merge_range('A7:D7', 'The objects in this document are filtered using the following services: {} and the following components: {}'.format(
            ", ".join([elem.name for elem in self.services]),
            ", ".join([elem.name for elem in self.components])))

    def generate_table_1(self, workbook, worksheet):
        worksheet.set_column('A1:B1', 20)
        worksheet.set_column('B1:C1', 50)
        worksheet.set_column('D1:K1', 25)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 20)
        worksheet.merge_range(
            'A1:K1', 'REQUIREMENTS AND THEIR DETAILS', self.format_header)
        headers = [
            'REQUIREMENT UID', 'REQUIREMENT', 'NOTE', 'DISSEMINATION', 'QUALITY CONTROL', 'GROUP',
            'UNCERTAINTY (%)', 'UPDATE FREQUENCY', 'TIMELINESS', 'SCALE', 'HORIZONTAL RESOLUTION'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        self.requirements = Requirement.objects.filter(
            products__in=self.products).distinct()
        index = 2
        for requirement in self.requirements:
            worksheet.set_row(index, 50)
            data = [
                requirement.id, requirement.name, requirement.note,
                requirement.dissemination.name, requirement.quality_control_procedure.name,
                requirement.group.name,
                '{}\n{}\n{}\n'.format(requirement.uncertainty.threshold,
                                      requirement.uncertainty.breakthrough, requirement.uncertainty.goal),
                '{}\n{}\n{}\n'.format(requirement.update_frequency.threshold,
                                      requirement.update_frequency.breakthrough, requirement.update_frequency.goal),
                '{}\n{}\n{}\n'.format(requirement.timeliness.threshold,
                                      requirement.timeliness.breakthrough, requirement.timeliness.goal),
                '{}\n{}\n{}\n'.format(
                    requirement.scale.threshold, requirement.scale.breakthrough, requirement.scale.goal),
                '{}\n{}\n{}\n'.format(requirement.horizontal_resolution.threshold,
                                      requirement.horizontal_resolution.breakthrough, requirement.horizontal_resolution.goal),
            ]
            worksheet.write_row(index, 0, data, self.format_rows)
            index += 1

    def generate_table_2(self, workbook, worksheet):
        worksheet.set_column('A1:A1', 20)
        worksheet.set_column('B1:B1', 120)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:B1', 'PRODUCTS AND THEIR DESCRIPTIONS', self.format_header)
        headers = ['PRODUCT', 'DESCRIPTION']
        worksheet.write_row('A2', headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            data = [product.name, product.description]
            worksheet.write_row(index, 0, data, self.format_rows)
            index += 1

    def generate_table_3(self, workbook, worksheet):
        worksheet.set_column('A1:B1', 20)
        worksheet.set_column('C1:C1', 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:C1', 'PRODUCTS AND ASSOCIATED REQUIREMENTS', self.format_header)
        headers = [
            'PRODUCT', 'REQUIREMENT', 'REQUIREMENT UID'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            requirements = product.product_requirements.all()
            requirement_count = requirements.count()
            if requirement_count >= 2:
                worksheet.merge_range(
                    index, 0, index + requirement_count - 1, 0, product.name, self.format_rows)
                for product_requirement in requirements.all():
                    data = [product_requirement.requirement.name,
                            product_requirement.requirement.id]
                    worksheet.write_row(index, 1, data, self.format_rows)
                    index += 1
            elif requirement_count == 1:
                requirement = requirements.first().requirement
                worksheet.write_row(
                    index, 0, [product.name, requirement.name, requirement.id], self.format_rows)
                index += 1
            else:
                worksheet.write_row(
                    index, 0, [product.name, '', ''], self.format_rows)
                index += 1

    def generate_table_4(self, workbook, worksheet):
        worksheet.set_column('A1:A1', 30)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:D1', 20)
        worksheet.set_column('E1:E1', 30)
        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:E1', 'DATASETS AND RELATED DATA PROVIDERS PER REQUIREMENT', self.format_header)
        headers = [
            'REQUIREMENT', 'REQUIREMENT UID', 'DATA', 'DATA PROVIDER', 'DATA PROVIDER TYPE'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        requirement_index = 2
        for requirement in self.requirements:
            data_index = requirement_index
            for datarequirement in requirement.datarequirement_set.all():
                provider_index = data_index
                for data_provider in datarequirement.data.providers.all():
                    worksheet.write_row(provider_index, 3, [data_provider.name, getattr(getattr(
                        data_provider.details.first(), 'provider_type', ''), 'name', '')], self.format_rows)
                    provider_index += 1
                if provider_index == data_index:
                    worksheet.write_row(
                        data_index, 2, [datarequirement.data.name, '', ''], self.format_rows)
                    data_index = provider_index
                elif provider_index == data_index + 1:
                    worksheet.write_row(
                        data_index, 2, [datarequirement.data.name], self.format_rows)
                else:
                    worksheet.merge_range(
                        data_index, 2, provider_index - 1, 2, datarequirement.data.name, self.format_rows)
                data_index = provider_index
            if data_index == requirement_index:
                worksheet.write_row(requirement_index, 0, [
                                    requirement.name, requirement.id, '', '', ''], self.format_rows)
                requirement_index = data_index + 1
            elif data_index == requirement_index + 1:
                worksheet.write_row(requirement_index, 0, [
                                    requirement.name, requirement.id], self.format_rows)
                requirement_index = data_index
            else:
                worksheet.merge_range(
                    requirement_index, 0, data_index - 1, 0, requirement.name, self.format_rows)
                worksheet.merge_range(
                    requirement_index, 1, data_index - 1, 1, requirement.id, self.format_rows)
                requirement_index = data_index

    def generate_table_5(self, workbook, worksheet):
        worksheet.set_column('A1:A1', 50)
        worksheet.set_column('B1:B1', 60)
        worksheet.set_column('C1:F1', 18)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:F1', 'MAIN DETAILS BETWEEN REQUIREMENTS AND PRODUCTS', self.format_header)
        headers = [
            'PRODUCT', 'REQUIREMENT', 'REQUIREMENT UID', 'BARRIER', 'RELEVANCE', 'CRITICALITY'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        index = 2
        for product in self.products:
            product_merge_dimension = product.product_requirements.all().count()
            if product_merge_dimension >= 2:
                worksheet.merge_range(
                    index, 0, index + product_merge_dimension - 1, 0, product.name, self.format_rows)
                for product_requirement in product.product_requirements.all():
                    data = [
                        product_requirement.requirement.name, product_requirement.requirement.id,
                        "\n".join([x.name for x in product_requirement.barriers.all(
                        )]), product_requirement.relevance.name,
                        product_requirement.criticality.name
                    ]
                    worksheet.write_row(index, 1, data, self.format_rows)
                    index += 1
            elif product_merge_dimension == 1:
                product_requirement = product.product_requirements.first()
                worksheet.write_row(index, 0, [product.name, product_requirement.requirement.name, product_requirement.requirement.id,
                                               "\n".join([x.name for x in product_requirement.barriers.all()]), product_requirement.relevance.name,
                                               product_requirement.criticality.name], self.format_rows)
                index += 1
            else:
                worksheet.write_row(
                    index, 0, [product.name, '', '', '', '', ''], self.format_rows)
                index += 1

    def generate_table_6(self, workbook, worksheet):
        worksheet.set_column('A1:C1', 40)
        worksheet.set_column('D1:D1', 60)
        worksheet.set_column('E1:E1', 40)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:E1', 'LEVEL OF COMPLIANCE BETWEEN DATASET AND REQUIREMENT', self.format_header)
        headers = [
            'PRODUCT', 'DATA', 'REQUIREMENT', 'REQUIREMENT UID', 'DATA LINK NOTE'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        product_index = 2
        for product in self.products:
            requirements = [
                x.requirement for x in product.product_requirements.all()]
            data = Data.objects.filter(
                requirements__in=requirements, datarequirement___deleted=False).distinct()
            data_index = product_index
            for data_object in data:
                data_requirement_index = data_index
                for data_requirement in data_object.datarequirement_set.all():
                    worksheet.write_row(data_requirement_index, 2, [
                                        data_requirement.requirement.name, data_requirement.requirement.id, data_requirement.note])
                    data_requirement_index += 1
                if data_index == data_requirement_index:
                    worksheet.write_row(
                        data_index, 1, [data_object.name, '', '', ''], self.format_rows)
                    data_index = data_requirement_index
                elif data_requirement_index == data_index + 1:
                    worksheet.write_row(
                        data_index, 1, [data_object.name], self.format_rows)
                else:
                    worksheet.merge_range(
                        data_index, 1, data_requirement_index - 1, 1, data_object.name, self.format_rows)
                data_index = data_requirement_index
            if data_index == product_index:
                worksheet.write_row(product_index, 0, [
                                    product.name, '', '', '', ''], self.format_rows)
                product_index = data_index + 1
            elif data_index == product_index + 1:
                worksheet.write_row(product_index, 0, [
                                    product.name], self.format_rows)
                product_index = data_index
            else:
                worksheet.merge_range(
                    product_index, 0, data_index - 1, 0, product.name, self.format_rows)
                product_index = data_index

    def generate_table_7(self, workbook, worksheet):
        worksheet.set_column('A1:A1', 40)
        worksheet.set_column('B1:F1', 20)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:F1', 'DATASET MAIN DETAILS', self.format_header)
        headers = [
            'DATA', 'DATA TYPE', 'DATA FORMAT', 'DATA UPDATE FREQUENCY', 'DATA AREA', 'DATA POLICY'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        data = Data.objects.filter(
            requirements__in=self.requirements, datarequirement___deleted=False).distinct()
        index = 2
        for data_object in data:
            row_data = [
                data_object.name,
                getattr(data_object.data_type, 'name', ''),
                getattr(data_object.data_format, 'name', ''),
                getattr(data_object.update_frequency, 'name', ''),
                getattr(data_object.area, 'name', ''),
                getattr(data_object.data_policy, 'name', '')
            ]
            worksheet.write_row(index, 0, row_data, self.format_rows)
            index += 1

    def generate_table_8(self, workbook, worksheet):
        worksheet.set_column('A1:B1', 40)
        worksheet.set_column('C1:F1', 25)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 17)
        worksheet.merge_range(
            'A1:F1', 'DATASETS AND RELATED DATA PROVIDERS', self.format_header)
        headers = [
            'DATA', 'DATA PROVIDER', 'DATA PROVIDER TYPE', 'DATA QUALITY CONTROL', 'DATA DISSEMINATION', 'DATA TIMELINESS'
        ]
        worksheet.write_row('A2', headers, self.format_cols_headers)
        data = Data.objects.filter(
            requirements__in=self.requirements, datarequirement___deleted=False).distinct()
        index = 2
        for data_object in data:
            provider_count = data_object.providers.all().count()
            if provider_count >= 2:
                worksheet.merge_range(
                    index, 0, index + provider_count - 1, 0, data_object.name, self.format_rows)
                for dataprovider in data_object.providers.all():
                    row_data = [
                        dataprovider.name,
                        getattr(getattr(dataprovider.details.first(),
                                        'provider_type', ''), 'name', ''),
                        getattr(data_object.quality_control_procedure,
                                'name', ''),
                        getattr(data_object.dissemination, 'name', ''), getattr(
                            data_object.timeliness, 'name', '')
                    ]
                    worksheet.write_row(index, 1, row_data, self.format_rows)
                    index += 1
            elif provider_count == 1:
                dataprovider = data_object.providers.first()
                row_data = [
                    data_object.name,
                    dataprovider.name,
                    getattr(getattr(dataprovider.details.first(),
                                    'provider_type', ''), 'name', ''),
                    getattr(data_object.quality_control_procedure, 'name', ''),
                    getattr(data_object.dissemination, 'name', ''), getattr(
                        data_object.timeliness, 'name', '')
                ]
                worksheet.write_row(index, 0, row_data, self.format_rows)
                index += 1
            else:
                worksheet.write_row(
                    index, 0, [data_object.name, '', '', '', '', ''], self.format_rows)
                index += 1

    def generate_excel_file(self, workbook):
        services = self.request.POST.getlist('service')
        components = self.request.POST.getlist('component')
        self.services = CopernicusService.objects.filter(id__in=services)
        self.components = Component.objects.filter(id__in=components)
        self.products = Product.objects.filter(component_id__in=components)
        self.set_formats(workbook)
        worksheet = workbook.add_worksheet('INTRODUCTION')
        self.generate_header_sheet(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 1')
        self.generate_table_1(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 2')
        self.generate_table_2(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 3')
        self.generate_table_3(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 4')
        self.generate_table_4(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 5')
        self.generate_table_5(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 6')
        self.generate_table_6(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 7')
        self.generate_table_7(workbook, worksheet)
        worksheet = workbook.add_worksheet('TABLE 8')
        self.generate_table_8(workbook, worksheet)
