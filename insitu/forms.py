from django import forms
from django.db import transaction

from insitu import models
from insitu import signals
from picklists.models import (
    Dissemination, QualityControlProcedure, RequirementGroup, ProductGroup
)


class CreatedByFormMixin:

    def save(self, created_by='', commit=True):
        if created_by:
            self.instance.created_by = created_by
        return super().save(commit)


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementBaseForm(forms.ModelForm):
    class Meta:
        model = models.ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'relevance', 'criticality', 'barriers']


class ProductRequirementForm(ProductRequirementBaseForm):
    product = forms.ModelChoiceField(disabled=True,
                                     queryset=models.Product.objects.all())


class RequirementProductRequirementForm(CreatedByFormMixin,
                                        ProductRequirementBaseForm):
    requirement = forms.ModelChoiceField(disabled=True,
                                         queryset=models.Requirement.objects.all())


class ProductRequirementEditForm(ProductRequirementForm,
                                 RequirementProductRequirementForm):
    pass


class ProductGroupRequirementForm(RequirementProductRequirementForm):
    product_group = forms.ModelChoiceField(queryset=ProductGroup.objects.all())

    class Meta:
        model = models.ProductRequirement
        exclude = ['product', 'created_by', 'state']

    def save(self, created_by='', commit=True):
        products = models.Product.objects.filter(
            group__name=self.cleaned_data['product_group'].name)
        self.cleaned_data.pop('product_group')
        barriers = self.cleaned_data.pop('barriers')
        self.cleaned_data['created_by'] = created_by
        for product in products:
            self.cleaned_data['product'] = product
            product_requirement = models.ProductRequirement.objects.create(
                **self.cleaned_data)
            product_requirement.barriers.add(*barriers)


class RequirementForm(forms.ModelForm):
    uncertainty_threshold = forms.CharField(max_length=100,
                                            required=False)
    uncertainty_breakthrough = forms.CharField(max_length=100,
                                               required=False)
    uncertainty_goal = forms.CharField(max_length=100,
                                       required=False)
    update_frequency_threshold = forms.CharField(max_length=100,
                                                 required=False)
    update_frequency_breakthrough = forms.CharField(max_length=100,
                                                    required=False)
    update_frequency_goal = forms.CharField(max_length=100,
                                            required=False)
    timeliness_threshold = forms.CharField(max_length=100,
                                           required=False)
    timeliness_breakthrough = forms.CharField(max_length=100,
                                              required=False)
    timeliness_goal = forms.CharField(max_length=100,
                                      required=False)
    horizontal_resolution_threshold = forms.CharField(max_length=100,
                                                      required=False)
    horizontal_resolution_breakthrough = forms.CharField(max_length=100,
                                                         required=False)
    horizontal_resolution_goal = forms.CharField(max_length=100,
                                                 required=False)
    vertical_resolution_threshold = forms.CharField(max_length=100,
                                                    required=False)
    vertical_resolution_breakthrough = forms.CharField(max_length=100,
                                                       required=False)
    vertical_resolution_goal = forms.CharField(max_length=100,
                                               required=False)

    class Meta:
        model = models.Requirement
        fields = ['name', 'note', 'dissemination',
                  'quality_control_procedure', 'group']

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
            result[attr] = data["_".join([metric, attr])]
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
        return self.cleaned_data

    def save(self, created_by='', commit=True):
        if created_by:
            self.instance.created_by = created_by

        uncertainty_data = self._get_metric_data('uncertainty', self.data)
        update_frequency_data = self._get_metric_data('update_frequency', self.data)
        timeliness_data = self._get_metric_data('timeliness', self.data)
        horizontal_resolution_data = self._get_metric_data('horizontal_resolution',
                                                           self.data)
        vertical_resolution_data = self._get_metric_data('vertical_resolution',
                                                         self.data)
        data = {
            'name': self.data['name'],
            'note': self.data['note'],
            'dissemination': Dissemination.objects.get(id=self.data['dissemination']),
            'quality_control_procedure':
                QualityControlProcedure.objects.get(
                    id=self.data['quality_control_procedure']
                ),
            'group': RequirementGroup.objects.get(id=self.data['group']),
        }

        if not self.initial:
            data['uncertainty'] = self._create_metric(**uncertainty_data)
            data['update_frequency'] = self._create_metric(**update_frequency_data)
            data['timeliness'] = self._create_metric(**timeliness_data)
            data['horizontal_resolution'] = self._create_metric(
                **horizontal_resolution_data)
            data['vertical_resolution'] = self._create_metric(**vertical_resolution_data)
            data['created_by'] = self.instance.created_by
            return models.Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(self.instance.update_frequency, **update_frequency_data)
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

    def clean(self):
        super().clean()
        cleaned_data = dict(self.cleaned_data)
        initial_data = dict(self.initial)
        cleaned_data.pop('name')
        initial_data.pop('name')
        if cleaned_data == initial_data:
            self.add_error(None, "This requirement is too similar.")
        return self.cleaned_data

    def save(self, created_by='', commit=True):
        self.initial = None
        return super().save(created_by, commit)


class DataForm(CreatedByFormMixin, forms.ModelForm):
    class Meta:
        model = models.Data
        auto_created = True
        fields = ['name', 'note', 'update_frequency', 'coverage',
                  'start_time_coverage', 'end_time_coverage', 'timeliness',
                  'policy', 'data_type', 'data_format',
                  'quality_control_procedure', 'dissemination',
                  'inspire_themes', 'essential_variables']


class DataRequirementBaseForm(forms.ModelForm):
    class Meta:
        model = models.DataRequirement
        fields = ['data', 'requirement', 'information_costs', 'handling_costs',
                  'note', 'level_of_compliance']


class DataRequirementForm(DataRequirementBaseForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())


class RequirementDataRequirementForm(CreatedByFormMixin,
                                     DataRequirementBaseForm):
    requirement = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Requirement.objects.all())


class DataRequirementEditForm(DataRequirementForm,
                              RequirementDataRequirementForm):
    pass


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
                self.add_error(None, 'Members should be different than the network.')
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
    class Meta:
        model = models.DataProviderRelation
        fields = ['data', 'provider', 'role']


class DataProviderRelationProviderForm(DataProviderRelationBaseForm):
    provider = forms.ModelChoiceField(
        disabled=True,
        queryset=models.DataProvider.objects.all())


class DataProviderRelationGroupForm(CreatedByFormMixin,
                                    DataProviderRelationBaseForm):
    data = forms.ModelChoiceField(
        disabled=True,
        queryset=models.Data.objects.all())


class DataProviderRelationEditForm(DataProviderRelationProviderForm,
                                      DataProviderRelationGroupForm):
    pass
