import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from copernicus.settings import COUNTRY_MEMBERSHIPS, DEFAULT_FROM_EMAIL, SITE_URL
from insitu import models
from insitu import signals
from picklists.models import ProductGroup, Country
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreatedByFormMixin:
    def save(self, created_by="", commit=True):
        if created_by:
            self.instance.created_by = created_by
        return super().save(commit)


class RequiredFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields_required = getattr(self.Meta, "fields_required", None)
        for key in fields_required:
            self.fields[key].required = True


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = [
            "acronym",
            "name",
            "description",
            "group",
            "component",
            "status",
            "area",
            "note",
        ]


class ProductRequirementBaseForm(forms.ModelForm):
    requirement = forms.ModelChoiceField(
        disabled=True, queryset=models.Requirement.objects.all()
    )

    class Meta:
        model = models.ProductRequirement
        fields = [
            "requirement",
            "product",
            "note",
            "level_of_definition",
            "relevance",
            "criticality",
            "barriers",
        ]


class RequirementProductRequirementForm(
    CreatedByFormMixin, ProductRequirementBaseForm
):
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        requirement = cleaned_data.get("requirement")
        relevance = cleaned_data.get("relevance")

        exists_relation = models.ProductRequirement.objects.filter(
            product=product, requirement=requirement, relevance=relevance
        ).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class ProductRequirementEditForm(ProductRequirementBaseForm):
    product = forms.ModelChoiceField(
        disabled=True, queryset=models.Product.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url", None)
        super(ProductRequirementEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ProductRequirementEditForm, self).clean()
        requirement = self.data["requirement"]
        product = self.data["product"]
        relevance = cleaned_data["relevance"]

        exists_relation = (
            models.ProductRequirement.objects.filter(
                product=product, requirement=requirement, relevance=relevance
            )
            .exclude(id=self.url)
            .exists()
        )
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class ProductGroupRequirementForm(ProductRequirementBaseForm):
    product_group = forms.ModelChoiceField(queryset=ProductGroup.objects.all())

    class Meta:
        model = models.ProductRequirement
        exclude = ["product", "created_by", "state", "owner_history"]

    def clean(self):
        cleaned_data = super().clean()
        if "product_group" not in cleaned_data:
            return
        products = models.Product.objects.filter(
            group__name=cleaned_data["product_group"].name
        )
        cleaned_products = [
            product
            for product in products
            if not models.ProductRequirement.objects.filter(
                product=product,
                requirement=cleaned_data["requirement"],
                relevance=cleaned_data["relevance"],
            ).exists()
        ]
        if not cleaned_products:
            raise forms.ValidationError(
                "A relation already exists for all products of this group."
            )
        self.products = cleaned_products

    def save(self, created_by="", commit=True):
        products = self.products
        self.cleaned_data.pop("product_group")
        barriers = self.cleaned_data.pop("barriers")
        self.cleaned_data["created_by"] = created_by
        for product in products:
            self.cleaned_data["product"] = product
            product_requirement = models.ProductRequirement.objects.create(
                **self.cleaned_data
            )
            product_requirement.barriers.add(*barriers)


class RequirementForm(forms.ModelForm):
    uncertainty__threshold = forms.CharField(max_length=100, required=False)
    uncertainty__breakthrough = forms.CharField(max_length=100, required=False)
    uncertainty__goal = forms.CharField(max_length=100, required=False)
    update_frequency__threshold = forms.CharField(max_length=100, required=False)
    update_frequency__breakthrough = forms.CharField(max_length=100, required=False)
    update_frequency__goal = forms.CharField(max_length=100, required=False)
    timeliness__threshold = forms.CharField(max_length=100, required=False)
    timeliness__breakthrough = forms.CharField(max_length=100, required=False)
    timeliness__goal = forms.CharField(max_length=100, required=False)
    scale__threshold = forms.CharField(
        max_length=100,
        required=False,
        error_messages={"invalid": "Scale threshold field must be a number."},
    )
    scale__breakthrough = forms.CharField(
        max_length=100,
        required=False,
        error_messages={"invalid": "Scale breakthrough field must be a number."},
    )
    scale__goal = forms.CharField(
        max_length=100,
        required=False,
        error_messages={"invalid": "Scale goal field must be a number."},
    )
    horizontal_resolution__threshold = forms.CharField(max_length=100, required=False)
    horizontal_resolution__breakthrough = forms.CharField(
        max_length=100, required=False
    )
    horizontal_resolution__goal = forms.CharField(max_length=100, required=False)
    vertical_resolution__threshold = forms.CharField(max_length=100, required=False)
    vertical_resolution__breakthrough = forms.CharField(max_length=100, required=False)
    vertical_resolution__goal = forms.CharField(max_length=100, required=False)

    class Meta:
        model = models.Requirement
        fields = [
            "name",
            "note",
            "dissemination",
            "quality_control_procedure",
            "essential_variables",
            "group",
            "status",
            "owner",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].help_text = (
            'Please avoid separating words with the character "_"'
        )

    def _clean_scale(self):
        check_fields = [
            ("scale__breakthrough", "Scale breakthrough"),
            ("scale__threshold", "Scale threshold"),
            ("scale__goal", "Scale goal"),
        ]

        for field, text in check_fields:
            pattern = re.compile("[0-9><:]*$")
            value = self.cleaned_data.get(field)
            if (
                not pattern.match(self.cleaned_data.get(field))
                and value != "N/A"
                and value != "TBD"
            ):
                self.add_error(
                    None,
                    (
                        f"{text} must contain only numbers, >, < or : or have "
                        f"the value N/A , TBD"
                    ),
                )

    def _create_metric(self, threshold, breakthrough, goal):
        return models.Metric.objects.create(
            threshold=threshold,
            breakthrough=breakthrough,
            goal=goal,
            created_by=self.instance.created_by,
        )

    def _update_metric(self, metric, threshold, breakthrough, goal):
        metric.threshold = threshold
        metric.breakthrough = breakthrough
        metric.goal = goal
        metric.save(update_fields=["threshold", "breakthrough", "goal"])
        return metric

    def _get_metric_data(self, metric, data):
        result = dict()
        for attr in ["threshold", "breakthrough", "goal"]:
            result[attr] = data.get("__".join([metric, attr]), "")
            if result[attr] is None:
                result[attr] = ""
            if type(result[attr]) is int:
                result[attr] = str(result[attr])
        return result

    def _clean_metric(self, metrics):
        for metric in metrics:
            metric_values = self._get_metric_data(metric, self.cleaned_data)
            if "".join(metric_values.values()).strip():
                return True
        self.add_error(None, "At least one metric is required.")

    def clean(self):
        super(RequirementForm, self).clean()
        metric_fields = [
            "uncertainty",
            "update_frequency",
            "timeliness",
            "scale",
            "horizontal_resolution",
            "vertical_resolution",
        ]
        self._clean_metric(metric_fields)
        self._clean_scale()
        fields = {
            field: v
            for field, v in self.cleaned_data.items()
            if field != "name" and field != "essential_variables"
        }
        if self.instance.id:
            exists = (
                models.Requirement.objects.filter(**fields)
                .exclude(id=self.instance.id)
                .exists()
            )
        else:
            exists = models.Requirement.objects.filter(**fields).exists()
        if exists:
            self.add_error(
                None,
                "This requirement is a duplicate. Please use the existing requirement.",
            )

        return self.cleaned_data

    def save(self, created_by="", commit=True):
        if created_by:
            self.instance.created_by = created_by
        uncertainty_data = self._get_metric_data("uncertainty", self.cleaned_data)
        update_frequency_data = self._get_metric_data(
            "update_frequency", self.cleaned_data
        )
        timeliness_data = self._get_metric_data("timeliness", self.cleaned_data)
        scale_data = self._get_metric_data("scale", self.cleaned_data)
        horizontal_resolution_data = self._get_metric_data(
            "horizontal_resolution", self.cleaned_data
        )
        vertical_resolution_data = self._get_metric_data(
            "vertical_resolution", self.cleaned_data
        )
        data = {
            "name": self.cleaned_data["name"],
            "note": self.cleaned_data["note"],
            "owner": self.cleaned_data["owner"],
            "dissemination": self.cleaned_data["dissemination"],
            "quality_control_procedure": self.cleaned_data[
                "quality_control_procedure"
            ],
            "group": self.cleaned_data["group"],
            "status": self.cleaned_data["status"],
        }
        essential_variables = self.cleaned_data.pop("essential_variables")

        if not self.initial:
            data["uncertainty"] = self._create_metric(**uncertainty_data)
            data["update_frequency"] = self._create_metric(**update_frequency_data)
            data["timeliness"] = self._create_metric(**timeliness_data)
            data["scale"] = self._create_metric(**scale_data)
            data["horizontal_resolution"] = self._create_metric(
                **horizontal_resolution_data
            )
            data["vertical_resolution"] = self._create_metric(
                **vertical_resolution_data
            )
            data["created_by"] = self.instance.created_by
            requirement = models.Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(
                self.instance.update_frequency, **update_frequency_data
            )
            self._update_metric(self.instance.timeliness, **timeliness_data)
            self._update_metric(self.instance.scale, **scale_data)
            self._update_metric(
                self.instance.horizontal_resolution, **horizontal_resolution_data
            )
            self._update_metric(
                self.instance.vertical_resolution, **vertical_resolution_data
            )

            requirement = models.Requirement.objects.filter(pk=self.instance.pk)
            requirement.update(**data)
            requirement = requirement.first()
            for essential_variable in requirement.essential_variables.all():
                requirement.essential_variables.remove(essential_variable)
            signals.requirement_updated.send(sender=requirement)
        for essential_variable in essential_variables:
            requirement.essential_variables.add(essential_variable.id)
        return requirement


class RequirementCloneForm(RequirementForm):
    def save(self, created_by="", commit=True):
        self.initial = None
        return super().save(created_by, commit)


class DataForm(CreatedByFormMixin, forms.ModelForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = [
            "name",
            "note",
            "update_frequency",
            "area",
            "start_time_coverage",
            "end_time_coverage",
            "timeliness",
            "data_policy",
            "data_type",
            "copernicus_service_product",
            "data_format",
            "quality_control_procedure",
            "dissemination",
            "inspire_themes",
            "geographical_coverage",
            "status",
        ]

    def save(self, created_by="", commit=True):
        if created_by:
            self.instance.created_by = created_by
        else:
            created_by = self.instance.created_by
        inspire_themes = self.cleaned_data.pop("inspire_themes")
        geographical_coverages = self.cleaned_data.pop("geographical_coverage")
        if not self.initial:
            data = models.Data.objects.create(
                created_by=created_by, **self.cleaned_data
            )

        else:
            data = models.Data.objects.filter(pk=self.instance.pk)
            data.update(created_by=created_by, **self.cleaned_data)
            data = data.first()
            for inspire_theme in data.inspire_themes.all():
                data.inspire_themes.remove(inspire_theme)
            for geographical_coverage in data.geographical_coverage.all():
                data.geographical_coverage.remove(geographical_coverage)

        for inspire_theme in inspire_themes:
            data.inspire_themes.add(inspire_theme.id)
        for geographical_coverage in geographical_coverages:
            data.geographical_coverage.add(geographical_coverage.code)
        return data


class DataCloneForm(DataForm):
    def save(self, created_by="", commit=True):
        self.initial = None
        return super(DataCloneForm, self).save(created_by, commit)


class DataReadyForm(RequiredFieldsMixin, DataForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = [
            "name",
            "note",
            "update_frequency",
            "area",
            "start_time_coverage",
            "end_time_coverage",
            "timeliness",
            "data_policy",
            "data_type",
            "copernicus_service_product",
            "data_format",
            "status",
            "quality_control_procedure",
            "dissemination",
            "inspire_themes",
            "geographical_coverage",
        ]
        fields_required = [
            "update_frequency",
            "area",
            "timeliness",
            "data_policy",
            "data_type",
            "data_format",
            "quality_control_procedure",
            "dissemination",
            "geographical_coverage",
        ]

    def clean(self):
        cleaned_data = super(DataReadyForm, self).clean()
        inspire_themes = cleaned_data.get("inspire_themes", [])
        if not inspire_themes:
            error = "At least one Inspire Theme is required."
            self.add_error("inspire_themes", error)


class DataReadyCloneForm(DataReadyForm):
    def save(self, created_by="", commit=True):
        self.initial = None
        return super(DataReadyCloneForm, self).save(created_by, commit)


class DataRequirementBaseForm(forms.ModelForm):
    requirement = forms.ModelChoiceField(
        disabled=True, queryset=models.Requirement.objects.all()
    )

    class Meta:
        model = models.DataRequirement
        fields = [
            "data",
            "requirement",
            "information_costs",
            "handling_costs",
            "note",
            "level_of_compliance",
        ]


class RequirementDataRequirementForm(CreatedByFormMixin, DataRequirementBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        requirement = cleaned_data.get("requirement")
        exists_relation = models.DataRequirement.objects.filter(
            data=data,
            requirement=requirement,
        ).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class DataRequirementEditForm(DataRequirementBaseForm):
    data = forms.ModelChoiceField(disabled=True, queryset=models.Data.objects.all())


class DataProviderNetworkForm(CreatedByFormMixin, forms.ModelForm):
    is_network = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    class Meta:
        model = models.DataProvider
        fields = [
            "name",
            "native_name",
            "edmo",
            "description",
            "countries",
            "is_network",
        ]


class DataProviderNetworkMembersForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        required=False, queryset=models.DataProvider.objects.all(), label="Members"
    )

    class Meta:
        model = models.DataProvider
        fields = ["members"]

    def __init__(self, *args, **kwargs):
        super(DataProviderNetworkMembersForm, self).__init__(*args, **kwargs)
        self.initial["members"] = self.instance.members.all()

    def clean_members(self):
        instance = self.instance
        clean_members = self.cleaned_data["members"]
        for member in clean_members:
            if instance.pk == member.pk:
                self.add_error(None, "Members should be different than the network.")
        return clean_members

    def save(self, commit=True):
        instance = self.instance
        if "members" in self.cleaned_data:
            with transaction.atomic():
                instance.members.clear()

                for member in self.cleaned_data["members"]:
                    instance.members.add(member)
        return instance


class DataProviderDetailsForm(CreatedByFormMixin, forms.ModelForm):
    data_provider = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=models.DataProvider.objects.all(),
        required=False,
    )
    email = forms.CharField(required=False)
    website = forms.URLField(required=False, widget=forms.TextInput)

    class Meta:
        model = models.DataProviderDetails
        fields = [
            "acronym",
            "website",
            "address",
            "phone",
            "email",
            "contact_person",
            "provider_type",
            "data_provider",
        ]


class DataProviderNonNetworkForm(CreatedByFormMixin, forms.ModelForm):
    networks = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.DataProvider.objects.filter(is_network=True),
        label="Networks",
    )

    class Meta:
        model = models.DataProvider
        fields = [
            "name",
            "native_name",
            "edmo",
            "description",
            "countries",
            "networks",
        ]

    def save(self, created_by="", commit=True):
        instance = super().save(created_by, commit)
        if "networks" in self.cleaned_data:
            for network in self.cleaned_data["networks"]:
                instance.networks.add(network)
        return instance


class DataProviderRelationBaseForm(forms.ModelForm):
    data = forms.ModelChoiceField(disabled=True, queryset=models.Data.objects.all())

    class Meta:
        model = models.DataProviderRelation
        fields = ["data", "provider", "role"]


class DataProviderRelationGroupForm(CreatedByFormMixin, DataProviderRelationBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        provider = cleaned_data.get("provider")
        exists_relation = models.DataProviderRelation.objects.filter(
            data=data, provider=provider
        ).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class DataProviderRelationEditForm(DataProviderRelationBaseForm):
    provider = forms.ModelChoiceField(
        disabled=True, queryset=models.DataProvider.objects.all()
    )


class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = ["requests"]
        labels = {
            "requests": _("Select users you want to send a teammate request to"),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(TeamForm, self).__init__(*args, **kwargs)
        team = models.Team.objects.filter(user=user).first()
        if not team:
            team = models.Team.objects.create(user=user)
        self.instance = team
        self.fields["requests"].queryset = models.User.objects.exclude(
            id=user.id
        ).exclude(id__in=[user.id for user in self.instance.teammates.all()])
        self.initial["requests"] = self.instance.requests.all()

    def send_mail_accept_request(self, sender, receiver):
        url = reverse("auth:accept_request", kwargs={"sender_user": sender.id})
        context = {
            "receiver": receiver,
            "sender": sender,
            "url": SITE_URL + url,
        }
        html_message = render_to_string("mails/teammate_request.html", context=context)
        message = render_to_string("mails/teammate_request.txt", context=context)
        send_mail(
            subject="CIS2 Teammate request",
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[receiver.email],
            html_message=html_message,
        )

    def save(self, commit=True):
        instance = self.instance
        if "requests" in self.cleaned_data:
            with transaction.atomic():
                for request in instance.requests.all():
                    if request not in self.cleaned_data["requests"]:
                        instance.requests.remove(request)
                for request in self.cleaned_data["requests"]:
                    if request not in instance.requests.all():
                        instance.requests.add(request)
                        self.send_mail_accept_request(instance.user, request)
        return instance


class StandardReportForm(forms.Form):
    service = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.CopernicusService.objects.all(),
        label="Service",
    )
    component = forms.ModelMultipleChoiceField(
        required=False, queryset=models.Component.objects.all(), label="Component"
    )


class CountryReportForm(forms.Form):
    country = forms.ModelChoiceField(
        required=True, queryset=Country.objects.all(), label="Select a country"
    )


class DataProviderDuplicatesReportForm(forms.Form):
    country = forms.ModelChoiceField(
        required=False,
        queryset=Country.objects.all(),
        label="Select a country",
        empty_label="All countries",
    )


class DataNetworkReportForm(forms.Form):
    country_memberships = forms.ChoiceField(
        required=False, choices=COUNTRY_MEMBERSHIPS
    )
    countries = forms.ModelMultipleChoiceField(
        required=True, queryset=Country.objects.all()
    )


DATABASE_OBJECTS = (
    ("Product", "Products"),
    ("Requirement", "Requirements"),
    ("Data", "Data"),
    ("DataProvider", "Data Providers"),
)


class StatisticsDataForm(forms.Form):
    start_date = forms.DateField(input_formats=["%d-%m-%Y"])
    end_date = forms.DateField(input_formats=["%d-%m-%Y"])
    selected_object = forms.ChoiceField(choices=DATABASE_OBJECTS)


class UserEditAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"


class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        self.fields["email"].required = True
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields["password1"].widget.attrs["autocomplete"] = "off"
        self.fields["password2"].widget.attrs["autocomplete"] = "off"

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Please retype your password"}
        )
    )

    class Meta:
        model = models.User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
        }


class UserActionsForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    users = forms.ModelMultipleChoiceField(
        required=False, queryset=models.User.objects.all()
    )
    states = forms.MultipleChoiceField(
        required=False,
        choices=(
            ("draft", "Draft"),
            ("changes", "Changes requested"),
            ("ready", "Ready for validation"),
            ("valid", "Valid"),
        ),
    )
    services = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.CopernicusService.objects.all(),
        help_text="""
            Only services or only components can be selected, not both.
            When selecting services, the components field will be emptied."
        """,
    )
    components = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Component.objects.all(),
        help_text="""
            Only services or only components can be selected, not both.
            When selecting components, the services field will be emptied."
        """,
    )

    def clean(self):
        cleaned_data = super().clean()
        services = cleaned_data.get("services")
        components = cleaned_data.get("components")
        if services and components:
            # Only do something if both fields are valid so far.
            raise ValidationError(
                "Selecting a combination of services and components is not allowed."
            )


class EntriesCountReportForm(forms.Form):
    entrusted_entities = forms.ModelMultipleChoiceField(
        required=False, queryset=models.EntrustedEntity.objects.all()
    )


class EntriesStateReportForm(forms.Form):
    entry_type = forms.ChoiceField(
        required=True,
        choices=(
            ("Product", "Product"),
            ("Requirement", "Requirement"),
            ("Data", "Data"),
            ("DataProvider", "Data Provider"),
        ),
    )
