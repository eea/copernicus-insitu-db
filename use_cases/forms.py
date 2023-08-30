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
            "themes",
            "country",
            "region",
            "locality",
            "state",
        ]


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = models.Reference
        fields = ["source", "date"]


ReferenceFormSet = forms.inlineformset_factory(
    models.UseCase,
    models.Reference,
    fields=["source", "date"],
    form=ReferenceForm,
    extra=1,
    can_delete=True,
)
