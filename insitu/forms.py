from django.forms import CharField, ModelForm, ModelChoiceField
from insitu.models import DataGroup, Metric, Product
from insitu.models import ProductRequirement, Requirement
from picklists.models import Dissemination, Quality


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementBaseForm(ModelForm):
    class Meta:
        model = ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']


class ProductRequirementForm(ProductRequirementBaseForm):
    product = ModelChoiceField(disabled=True,
                               queryset=Product.objects.all())


class RequirementProductRequirementForm(ProductRequirementBaseForm):
    requirement = ModelChoiceField(disabled=True,
                                   queryset=Requirement.objects.all())


class ProductRequirementEditForm(ProductRequirementForm,
                                 RequirementProductRequirementForm):
    pass


class RequirementForm(ModelForm):
    uncertainty_threshold = CharField(max_length=100)
    uncertainty_breakthrough = CharField(max_length=100)
    uncertainty_goal = CharField(max_length=100)
    frequency_threshold = CharField(max_length=100)
    frequency_breakthrough = CharField(max_length=100)
    frequency_goal = CharField(max_length=100)
    timeliness_threshold = CharField(max_length=100)
    timeliness_breakthrough = CharField(max_length=100)
    timeliness_goal = CharField(max_length=100)
    horizontal_resolution_threshold = CharField(max_length=100)
    horizontal_resolution_breakthrough = CharField(max_length=100)
    horizontal_resolution_goal = CharField(max_length=100)
    vertical_resolution_threshold = CharField(max_length=100)
    vertical_resolution_breakthrough = CharField(max_length=100)
    vertical_resolution_goal = CharField(max_length=100)

    class Meta:
        model = Requirement
        fields = ['name', 'note', 'dissemination', 'quality']

    def _create_metric(self, threshold, breakthrough, goal):
        return Metric.objects.create(
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
            return Requirement.objects.create(**data)
        else:
            self._update_metric(self.instance.uncertainty, **uncertainty_data)
            self._update_metric(self.instance.frequency, **frequency_data)
            self._update_metric(self.instance.timeliness, **timeliness_data)
            self._update_metric(self.instance.horizontal_resolution,
                                **horizontal_resolution_data)
            self._update_metric(self.instance.vertical_resolution,
                                **vertical_resolution_data)
            return Requirement.objects.filter(pk=self.instance.pk).update(**data)


class DataGroupForm(ModelForm):
    class Meta:
        model = DataGroup
        auto_created = True
        fields = ['name', 'note', 'frequency', 'coverage', 'timeliness',
                  'policy', 'data_type', 'data_format', 'quality',
                  'inspire_themes']
