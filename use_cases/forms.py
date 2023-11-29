from django import forms
from use_cases import models


class UseCaseForm(forms.ModelForm):
    class Meta:
        model = models.UseCase
        fields = [
            "title",
            "data_provider",
            "data",
            "image",
            "image_description",
            "description",
            "copernicus_services",
            "components",
            "themes",
            "country",
            "region",
            "locality",
        ]


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = models.Reference
        fields = ["source", "link", "date"]
        widgets = {
          'source': forms.Textarea(attrs={'rows':2, 'cols':30}),
        }


ReferenceFormSet = forms.inlineformset_factory(
    models.UseCase,
    models.Reference,
    fields=["source", "link", "date"],
    form=ReferenceForm,
    extra=1,
    can_delete=True,
)
