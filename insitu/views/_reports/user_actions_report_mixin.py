from insitu.views._reports.base import BaseExcelMixin
from insitu.models import (
    Product,
    Requirement,
    Data,
    DataProvider,
    ProductRequirement,
    DataRequirement,
    DataProviderRelation,
    Component,
    LoggedAction,
)


class UserActionsReportMixin(BaseExcelMixin):
    # Mapping of object types to their respective model classes and filtered data keys
    # [logged_type] : (model_class, filtered_data_key)
    OBJECTS_MAPPING = {
        "product": (Product, "products"),
        "requirement": (Requirement, "requirements"),
        "data": (Data, "data"),
        "data provider": (DataProvider, "data_providers"),
        "data provider network": (DataProvider, "data_providers"),
        "relation between product and requirement": (
            ProductRequirement,
            "product_requirements",
        ),
        "relation between data and requirement": (
            DataRequirement,
            "data_requirements",
        ),
        "relation between data and data provider": (
            DataProviderRelation,
            "data_provider_relations",
        ),
    }

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

    def check_object(self, obj_id, obj_type, filtered_data=None):
        if obj_type in self.OBJECTS_MAPPING:
            if obj_id not in filtered_data[self.OBJECTS_MAPPING[obj_type][1]]:
                return False
        return True

    def get_object(self, obj_id, obj_type):
        if obj_id:
            if obj_type in self.OBJECTS_MAPPING:
                return (
                    self.OBJECTS_MAPPING[obj_type][0]
                    .objects.really_all()
                    .filter(id=obj_id)
                    .first()
                )

    def get_filtered_data(self, data):
        filtered_data = {}
        components = None
        if data["services"]:
            components = Component.objects.filter(service__in=data["services"])
        if data["components"]:
            components = Component.objects.filter(id__in=data["components"])
        if components:
            filtered_data["products"] = (
                Product.objects.really_all()
                .filter(component__in=components)
                .values_list("id", flat=True)
            )
            product_requirements = (
                ProductRequirement.objects.really_all()
                .filter(product_id__in=filtered_data["products"])
                .distinct()
            )
            filtered_data["product_requirements"] = product_requirements.values_list(
                "id", flat=True
            )
            filtered_data["requirements"] = product_requirements.values_list(
                "requirement_id", flat=True
            )
            data_requirements = (
                DataRequirement.objects.really_all()
                .filter(requirement_id__in=filtered_data["requirements"])
                .distinct()
            )
            filtered_data["data_requirements"] = data_requirements.values_list(
                "id", flat=True
            )
            filtered_data["data"] = data_requirements.values_list("data_id", flat=True)
            data_provider_relations = (
                DataProviderRelation.objects.really_all()
                .filter(data_id__in=filtered_data["data"])
                .distinct()
            )
            filtered_data["data_provider_relations"] = (
                data_provider_relations.values_list("id", flat=True)
            )
            filtered_data["data_providers"] = data_provider_relations.values_list(
                "provider_id", flat=True
            )
        return filtered_data

    def generate_worksheets(self, workbook, data):
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
        filtered_data = self.get_filtered_data(data)
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
                if filtered_data:
                    include_log = self.check_object(
                        int(logged_action.id_target),
                        logged_action.target_type,
                        filtered_data,
                    )
                    if not include_log:
                        continue
                target = self.get_object(
                    logged_action.id_target, logged_action.target_type
                )

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
