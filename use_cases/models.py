# from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
from django.db import models
from django_fsm import FSMField, transition
from django.conf import settings

from insitu import models as copernicus_models

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


def check_owner_user(instance, user):
    return user == instance.created_by


def check_user_is_publisher(instance, user):
    return user.groups.filter(name=settings.USE_CASES_PUBLISHER_GROUP).exists()


def check_can_return_to_draft(instance, user):
    if (
        instance.state == "published"
        and user.groups.filter(name=settings.USE_CASES_PUBLISHER_GROUP).exists()
    ):
        return True
    if (
        instance.state in ["changes", "publication_requested"]
        and user == instance.created_by
    ):
        return True


class UseCase(models.Model):
    title = models.CharField(max_length=256)
    data_provider = models.ForeignKey(
        copernicus_models.DataProvider, on_delete=models.SET_NULL, null=True
    )
    data = models.CharField(max_length=128)
    image = models.ImageField(
        upload_to="use-case-images/",
        verbose_name="Image",
        blank=True,
        null=True,
        help_text="Image used for this use case.",
    )
    image_description = models.TextField(null=True)
    description = models.TextField(null=True)
    copernicus_service = models.ForeignKey(
        copernicus_models.CopernicusService, on_delete=models.SET_NULL, null=True
    )
    components = models.ManyToManyField(
        copernicus_models.Component, blank=True, null=True
    )
    themes = models.ManyToManyField(Theme, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    region = models.CharField(max_length=256, blank=True)
    locality = models.CharField(max_length=256, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = FSMField(default="draft")
    feedback = models.TextField(blank=True)

    @property
    def get_state_title(self):
        return self.state.title().replace("_", " ")

    @transition(
        field=state,
        source="draft",
        target="publication_requested",
        permission=check_owner_user,
    )
    def request_publication(self):
        pass

    @transition(
        field=state,
        source="publication_requested",
        target="published",
        permission=check_user_is_publisher,
    )
    def publish(self):
        pass

    @transition(
        field=state,
        source=["publication_requested", "changes", "published"],
        target="draft",
        permission=check_can_return_to_draft,
    )
    def return_to_draft(self):
        pass

    @transition(
        field=state,
        source="publication_requested",
        target="changes",
        permission=check_user_is_publisher,
    )
    def request_changes(self):
        pass

    def __str__(self):
        return self.title


class Reference(models.Model):
    source = models.TextField(max_length=256)
    link = models.URLField(max_length=512, blank=True)
    use_case = models.ForeignKey(UseCase, on_delete=models.CASCADE)
    date = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source
