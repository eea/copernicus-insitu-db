from django import forms
from insitu import models
from picklists.models import Dissemination, Quality


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementBaseForm(forms.ModelForm):
    class Meta:
        model = models.ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']


class ProductRequirementForm(ProductRequirementBaseForm):
    product = forms.ModelChoiceField(disabled=True,
                                     queryset=models.Product.objects.all())


class RequirementProductRequirementForm(ProductRequirementBaseForm):
    requirement = forms.ModelChoiceField(disabled=True,
                                         queryset=models.Requirement.objects.all())


class ProductRequirementEditForm(ProductRequirementForm,
                                 RequirementProductRequirementForm):
    pass


class RequirementForm(forms.ModelForm):
    uncertainty_threshold = forms.CharField(max_length=100)
    uncertainty_breakthrough = forms.CharField(max_length=100)
    uncertainty_goal = forms.CharField(max_length=100)
    frequency_threshold = forms.CharField(max_length=100)
    frequency_breakthrough = forms.CharField(max_length=100)
    frequency_goal = forms.CharField(max_length=100)
    timeliness_threshold = forms.CharField(max_length=100)
    timeliness_breakthrough = forms.CharField(max_length=100)
    timeliness_goal = forms.CharField(max_length=100)
    horizontal_resolution_threshold = forms.CharField(max_length=100)
    horizontal_resolution_breakthrough = forms.CharField(max_length=100)
    horizontal_resolution_goal = forms.CharField(max_length=100)
    vertical_resolution_threshold = forms.CharField(max_length=100)
    vertical_resolution_breakthrough = forms.CharField(max_length=100)
    vertical_resolution_goal = forms.CharField(max_length=100)

    class Meta:
        model = models.Requirement
        fields = ['name', 'note', 'dissemination', 'quality']

    def _create_metric(self, threshold, breakthrough, goal):
        return models.Metric.objects.create(
            threshold=threshold,
            breakthrough=breakthrough,
            goal=goal
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

    def save(self, commit=True):
        uncertainty_data = self._get_metric_data('uncertainty', self.data)
        frequency_data = self._get_metric_data('frequency', self.data)
        timeliness_data = self._get_metric_data('timeliness', self.data)
        horizontal_resolution_data = self._get_metric_data('horizontal_resolution',
                                                           self.data)
        vertical_resolution_data = self._get_metric_data('vertical_resolution',
                                                         self.data)
        data = {
            'name': self.data['name'],
            'note': self.data['note'],
            'dissemination': Dissemination.objects.get(id=self.data['dissemination']),
            'quality': Quality.objects.get(id=self.data['quality'])
        }

        if not self.initial:
            data['uncertainty'] = self._create_metric(**uncertainty_data)
            data['frequency'] = self._create_metric(**frequency_data)
            data['timeliness'] = self._create_metric(**timeliness_data)
            data['horizontal_resolution'] = self._create_metric(
                **horizontal_resolution_data)
            data['vertical_resolution'] = self._create_metric(**vertical_resolution_data)
            return models.Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(self.instance.frequency, **frequency_data)
            self._update_metric(self.instance.timeliness, **timeliness_data)
            self._update_metric(self.instance.horizontal_resolution,
                                **horizontal_resolution_data)
            self._update_metric(self.instance.vertical_resolution,
                                **vertical_resolution_data)
            return models.Requirement.objects.filter(pk=self.instance.pk).update(**data)


class DataGroupForm(forms.ModelForm):
    class Meta:
        model = models.DataGroup
        auto_created = True
        fields = ['name', 'note', 'frequency', 'coverage', 'timeliness',
                  'policy', 'data_type', 'data_format', 'quality',
                  'inspire_themes', 'essential_climate_variables']
