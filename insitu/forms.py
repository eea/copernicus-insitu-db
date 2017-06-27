from django.forms import HiddenInput, ModelForm

from insitu.models import Product, ProductRequirement


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['acronym', 'name', 'description', 'group', 'component',
                  'status', 'coverage', 'note']


class ProductRequirementForm(ModelForm):
    class Meta:
        model = ProductRequirement
        fields = ['requirement', 'product', 'note', 'level_of_definition',
                  'distance_to_target', 'relevance', 'criticality',
                  'barriers']
        widgets = {
            'product': HiddenInput()
        }
