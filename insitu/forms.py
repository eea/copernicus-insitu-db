from django import forms
from django.db import transaction

from insitu import models
from insitu import signals
from picklists.models import (
    ProductGroup,
)


class CreatedByFormMixin:
    def save(self, created_by='', commit=True):
        if created_by:
            self.instance.created_by = created_by
        return super().save(commit)


class RequiredFieldsMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields_required = getattr(self.Meta, 'fields_required', None)
        for key in fields_required:
            self.fields[key].required = True


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'area', 'note']


class ProductRequirementBaseForm(forms.ModelForm):
    requirement = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Requirement.objects.all()
    )

    class Meta:
        model = models.ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'relevance', 'criticality', 'barriers']


class RequirementProductRequirementForm(CreatedByFormMixin,
                                        ProductRequirementBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        requirement = cleaned_data.get('requirement')
        relevance = cleaned_data.get('relevance')

        exists_relation = models.ProductRequirement.objects.filter(
            product=product,
            requirement=requirement,
            relevance=relevance
        ).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class ProductRequirementEditForm(ProductRequirementBaseForm):
    product = forms.ModelChoiceField(disabled=True,
                                     queryset=models.Product.objects.all())

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', None)
        super(ProductRequirementEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ProductRequirementEditForm, self).clean()

        requirement = self.data['requirement']
        product = self.data['product']
        relevance = cleaned_data['relevance']

        exists_relation = models.ProductRequirement.objects.filter(
            product=product,
            requirement=requirement,
            relevance=relevance
        ).exclude(id=self.url).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class ProductGroupRequirementForm(ProductRequirementBaseForm):
    product_group = forms.ModelChoiceField(queryset=ProductGroup.objects.all())

    class Meta:
        model = models.ProductRequirement
        exclude = ['product', 'created_by', 'state']

    def clean(self):
        cleaned_data = super().clean()
        if 'product_group' not in cleaned_data:
            return
        products = models.Product.objects.filter(
            group__name=cleaned_data['product_group'].name)
        cleaned_products = [
            product for product in products if not
            models.ProductRequirement.objects.filter(
                product=product,
                requirement=cleaned_data['requirement'],
                relevance=cleaned_data['relevance']
            ).exists()
        ]
        if not cleaned_products:
            raise forms.ValidationError(
                "A relation already exists for all products of this group."
            )
        self.products = cleaned_products

    def save(self, created_by='', commit=True):
        products = self.products
        self.cleaned_data.pop('product_group')
        barriers = self.cleaned_data.pop('barriers')
        self.cleaned_data['created_by'] = created_by
        for product in products:
            self.cleaned_data['product'] = product
            product_requirement = models.ProductRequirement.objects.create(
                **self.cleaned_data)
            product_requirement.barriers.add(*barriers)


class RequirementForm(forms.ModelForm):
    uncertainty__threshold = forms.CharField(max_length=100,
                                             required=False)
    uncertainty__breakthrough = forms.CharField(max_length=100,
                                                required=False)
    uncertainty__goal = forms.CharField(max_length=100,
                                        required=False)
    update_frequency__threshold = forms.CharField(max_length=100,
                                                  required=False)
    update_frequency__breakthrough = forms.CharField(max_length=100,
                                                     required=False)
    update_frequency__goal = forms.CharField(max_length=100,
                                             required=False)
    timeliness__threshold = forms.CharField(max_length=100,
                                            required=False)
    timeliness__breakthrough = forms.CharField(max_length=100,
                                               required=False)
    timeliness__goal = forms.CharField(max_length=100,
                                       required=False)
    horizontal_resolution__threshold = forms.CharField(max_length=100,
                                                       required=False)
    horizontal_resolution__breakthrough = forms.CharField(max_length=100,
                                                          required=False)
    horizontal_resolution__goal = forms.CharField(max_length=100,
                                                  required=False)
    vertical_resolution__threshold = forms.CharField(max_length=100,
                                                     required=False)
    vertical_resolution__breakthrough = forms.CharField(max_length=100,
                                                        required=False)
    vertical_resolution__goal = forms.CharField(max_length=100,
                                                required=False)

    class Meta:
        model = models.Requirement
        fields = ['name', 'note', 'dissemination',
                  'quality_control_procedure', 'group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = (
            'Please avoid separating words with the character "_"')

    def _create_metric(self, threshold, breakthrough, goal):
        return models.Metric.objects.create(
            threshold=threshold,
            breakthrough=breakthrough,
            goal=goal,
            created_by=self.instance.created_by
        )

    def _update_metric(self, metric, threshold, breakthrough, goal):
        metric.threshold = threshold
        metric.breakthrough = breakthrough
        metric.goal = goal
        metric.save(update_fields=['threshold', 'breakthrough', 'goal'])
        return metric

    def _get_metric_data(self, metric, data):
        result = dict()
        for attr in ['threshold', 'breakthrough', 'goal']:
            result[attr] = data["__".join([metric, attr])]
        return result

    def _clean_metric(self, metrics):
        for metric in metrics:
            metric_values = self._get_metric_data(metric, self.cleaned_data)
            if "".join(metric_values.values()).strip():
                return True
        self.add_error(None, "At least one metric is required.")

    def clean(self):
        super(RequirementForm, self).clean()
        metric_fields = ['uncertainty', 'update_frequency', 'timeliness',
                         'horizontal_resolution', 'vertical_resolution']
        self._clean_metric(metric_fields)
        fields = {field: v for field, v in self.cleaned_data.items()
                  if field != 'name'}
        if self.instance.id:
            exists = len(models.Requirement.objects.filter(**fields)) > 1
        else:
            exists = models.Requirement.objects.filter(**fields).exists()
        if exists:
            self.add_error(
                None,
                "This requirement is a duplicate. Please use the existing requirement."
            )

        return self.cleaned_data

    def save(self, created_by='', commit=True):
        if created_by:
            self.instance.created_by = created_by
        uncertainty_data = self._get_metric_data('uncertainty', self.cleaned_data)
        update_frequency_data = self._get_metric_data(
            'update_frequency',
            self.cleaned_data
        )
        timeliness_data = self._get_metric_data('timeliness', self.cleaned_data)
        horizontal_resolution_data = self._get_metric_data(
            'horizontal_resolution',
            self.cleaned_data
        )
        vertical_resolution_data = self._get_metric_data('vertical_resolution',
                                                         self.cleaned_data)
        data = {
            'name': self.cleaned_data['name'],
            'note': self.cleaned_data['note'],
            'dissemination': self.cleaned_data['dissemination'],
            'quality_control_procedure':
                self.cleaned_data['quality_control_procedure'],
            'group': self.cleaned_data['group'],
        }

        if not self.initial:
            data['uncertainty'] = self._create_metric(**uncertainty_data)
            data['update_frequency'] = self._create_metric(
                **update_frequency_data)
            data['timeliness'] = self._create_metric(**timeliness_data)
            data['horizontal_resolution'] = self._create_metric(
                **horizontal_resolution_data)
            data['vertical_resolution'] = self._create_metric(
                **vertical_resolution_data)
            data['created_by'] = self.instance.created_by
            return models.Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(self.instance.update_frequency,
                                **update_frequency_data)
            self._update_metric(self.instance.timeliness, **timeliness_data)
            self._update_metric(self.instance.horizontal_resolution,
                                **horizontal_resolution_data)
            self._update_metric(self.instance.vertical_resolution,
                                **vertical_resolution_data)

            reqs = models.Requirement.objects.filter(pk=self.instance.pk)
            result = reqs.update(**data)
            for requirement in reqs:
                signals.requirement_updated.send(sender=requirement)
            return result


class RequirementCloneForm(RequirementForm):
    def save(self, created_by='', commit=True):
        self.initial = None
        return super().save(created_by, commit)


class DataForm(CreatedByFormMixin, forms.ModelForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = ['name', 'note', 'update_frequency', 'area',
                  'start_time_coverage', 'end_time_coverage', 'timeliness',
                  'data_policy', 'data_type', 'data_format',
                  'quality_control_procedure', 'dissemination',
                  'inspire_themes', 'essential_variables']

    def save(self, created_by='', commit=True):
        if created_by:
            self.instance.created_by = created_by
        else:
            created_by = self.instance.created_by
        inspire_themes = self.cleaned_data.pop('inspire_themes')
        essential_variables = self.cleaned_data.pop('essential_variables')
        if not self.initial:
            data = models.Data.objects.create(created_by=created_by,
                                              **self.cleaned_data)

        else:
            data = models.Data.objects.filter(pk=self.instance.pk)
            data.update(created_by=created_by, **self.cleaned_data)
            data = data.first()
            for inspire_theme in data.inspire_themes.all():
                data.inspire_themes.remove(inspire_theme)
            for essential_variable in data.essential_variables.all():
                data.essential_variables.remove(essential_variable)

        for inspire_theme in inspire_themes:
            data.inspire_themes.add(inspire_theme.id)
        for essential_variable in essential_variables:
            data.essential_variables.add(essential_variable.id)
        return data

class DataCloneForm(DataForm):
    def save(self, created_by='', commit=True):
        self.initial = None
        return super(DataCloneForm, self).save(created_by, commit)


class DataReadyForm(RequiredFieldsMixin, DataForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = ['name', 'note', 'update_frequency', 'area',
                  'start_time_coverage', 'end_time_coverage', 'timeliness',
                  'data_policy', 'data_type', 'data_format',
                  'quality_control_procedure', 'dissemination',
                  'inspire_themes', 'essential_variables']
        fields_required = ['update_frequency', 'area', 'timeliness',
                           'data_policy', 'data_type', 'data_format',
                           'quality_control_procedure', 'dissemination']

    def clean(self):
        cleaned_data = super(DataReadyForm, self).clean()
        inspire_themes = cleaned_data.get("inspire_themes", [])
        essential_variables = cleaned_data.get("essential_variables", [])
        if not inspire_themes and not essential_variables:
            error = "At least one Inspire Theme or Essential Variable is required."
            self.add_error("inspire_themes", '')
            self.add_error("essential_variables", error)


class DataReadyCloneForm(DataReadyForm):
    def save(self, created_by='', commit=True):
        self.initial = None
        return super(DataReadyCloneForm, self).save(created_by, commit)


class DataRequirementBaseForm(forms.ModelForm):
    requirement = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Requirement.objects.all())

    class Meta:
        model = models.DataRequirement
        fields = ['data', 'requirement', 'information_costs', 'handling_costs',
                  'note', 'level_of_compliance']


class RequirementDataRequirementForm(CreatedByFormMixin,
                                     DataRequirementBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        requirement = cleaned_data.get('requirement')
        exists_relation = models.DataRequirement.objects.filter(
            data=data,
            requirement=requirement,
        ).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class DataRequirementEditForm(DataRequirementBaseForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())


class DataProviderNetworkForm(CreatedByFormMixin, forms.ModelForm):
    is_network = forms.BooleanField(initial=True,
                                    widget=forms.HiddenInput)

    class Meta:
        model = models.DataProvider
        fields = ['name', 'description', 'countries', 'is_network']


class DataProviderNetworkMembersForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.DataProvider.objects.all(),
        label='Members')

    class Meta:
        model = models.DataProvider
        fields = ['members']

    def __init__(self, *args, **kwargs):
        super(DataProviderNetworkMembersForm, self).__init__(*args, **kwargs)
        self.initial['members'] = self.instance.members.all()

    def clean_members(self):
        instance = self.instance
        clean_members = self.cleaned_data['members']
        for member in clean_members:
            if instance.pk == member.pk:
                self.add_error(None,
                               'Members should be different than the network.')
        return clean_members

    def save(self, commit=True):
        instance = self.instance
        if 'members' in self.cleaned_data:
            with transaction.atomic():
                instance.members.clear()

                for member in self.cleaned_data['members']:
                    instance.members.add(member)
        return instance


class DataProviderDetailsForm(CreatedByFormMixin, forms.ModelForm):
    data_provider = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=models.DataProvider.objects.filter(is_network=False),
        required=False)
    email = forms.CharField(required=False)
    website = forms.URLField(required=False, widget=forms.TextInput)

    class Meta:
        model = models.DataProviderDetails
        fields = ['acronym', 'website', 'address', 'phone', 'email',
                  'contact_person', 'provider_type', 'data_provider']


class DataProviderNonNetworkForm(CreatedByFormMixin, forms.ModelForm):
    networks = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.DataProvider.objects.filter(is_network=True),
        label='Networks')

    class Meta:
        model = models.DataProvider
        fields = ['name', 'description', 'countries', 'networks']

    def save(self, created_by='', commit=True):
        instance = super().save(created_by, commit)
        if 'networks' in self.cleaned_data:
            for network in self.cleaned_data['networks']:
                instance.networks.add(network)
        return instance


class DataProviderRelationBaseForm(forms.ModelForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())

    class Meta:
        model = models.DataProviderRelation
        fields = ['data', 'provider', 'role']


class DataProviderRelationGroupForm(CreatedByFormMixin,
                                    DataProviderRelationBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        provider = cleaned_data.get('provider')
        exists_relation = models.DataProviderRelation.objects.filter(
            data=data,
            provider=provider).exists()
        if exists_relation:
            raise forms.ValidationError("This relation already exists.")


class DataProviderRelationEditForm(DataProviderRelationBaseForm):
    provider = forms.ModelChoiceField(
        disabled=True,
        queryset=models.DataProvider.objects.all())


class TeamForm(forms.ModelForm):

    class Meta:
        model = models.Team
        fields = ['teammates']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TeamForm, self).__init__(*args, **kwargs)
        team = models.Team.objects.filter(user=user).first()
        if not team:
            team = models.Team.objects.create(user=user)
        self.instance = team
        self.initial['teammates'] = self.instance.teammates.all()

    def clean_teammates(self):
        instance = self.instance
        clean_teammates = self.cleaned_data['teammates']
        for teammate in clean_teammates:
            if instance.user.pk == teammate.pk:
                self.add_error(None,
                               'You cannot be your own teammate.')
        return clean_teammates

    def save(self, commit=True):
        instance = self.instance
        if 'teammates' in self.cleaned_data:
            with transaction.atomic():
                for teammate in instance.teammates.all():
                    if teammate not in self.cleaned_data['teammates']:
                        team = models.Team.objects.filter(user=teammate).first()
                        if not team:
                            models.Team.objects.create(user=teammate)
                        teammate.team.teammates.remove(instance.user)
                instance.teammates.clear()
                for teammate in self.cleaned_data['teammates']:
                    instance.teammates.add(teammate)
                    team = models.Team.objects.filter(user=teammate).first()
                    if not team:
                        team = models.Team.objects.create(user=teammate)
                    team.teammates.add(instance.user)
        return instance
