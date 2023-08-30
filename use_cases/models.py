# from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


def user_model_str(self):
    return "{} {}".format(self.first_name, self.last_name)


User.add_to_class("__str__", user_model_str)


class CopernicusService(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class Theme(models.Model):
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UseCase(models.Model):
    title = models.CharField(max_length=256)
    data_provider = models.CharField(max_length=256)
    data = models.CharField(max_length=128)
    image = models.ImageField(
        upload_to="use-case-images/",
        verbose_name="Image",
        blank=True,
        null=True,
        help_text="Image used for this use case.",
    )
    image_description = models.CharField(max_length=512)
    description = models.CharField(max_length=512)
    copernicus_services = models.ManyToManyField(CopernicusService)
    themes = models.ManyToManyField(Theme, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    region = models.CharField(max_length=256)
    locality = models.CharField(max_length=256)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Reference(models.Model):
    source = models.CharField(max_length=256)
    use_case = models.ForeignKey(UseCase, on_delete=models.SET_NULL, null=True)
    date = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source
