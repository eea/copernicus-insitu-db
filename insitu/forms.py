from django.forms import CharField, HiddenInput, ModelForm, ModelChoiceField
from insitu.models import Product, ProductRequirement, Requirement


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
