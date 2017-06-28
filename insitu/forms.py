from django.forms import HiddenInput, ModelForm, ModelChoiceField

from insitu.models import Product, ProductRequirement, Requirement


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementForm(ModelForm):
    product = ModelChoiceField(disabled=True,
                               queryset=Product.objects.all())

    class Meta:
        model = ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']


class RequirementProductRequirementForm(ModelForm):
    requirement = ModelChoiceField(disabled=True,
                                   queryset=Requirement.objects.all())

    class Meta:
        model = ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']


class ProductRequirementEditForm(ModelForm):
    requirement = ModelChoiceField(disabled=True,
                                   queryset=Requirement.objects.all())
    product = ModelChoiceField(disabled=True,
                               queryset=Product.objects.all())

    class Meta:
        model = ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']
