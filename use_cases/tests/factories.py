from factory import SubFactory, RelatedFactory
from factory.django import DjangoModelFactory

from insitu.tests.base.insitu_factories import UserFactory
from use_cases import models

from factory import Sequence
from factory.django import ImageField


class CopernicusServiceFactory(DjangoModelFactory):
    name = Sequence(lambda n: "CopernicusService #{}".format(n))

    class Meta:
        model = models.CopernicusService


class CountryFactory(DjangoModelFactory):
    code = Sequence(lambda n: "%s" % n)
    name = Sequence(lambda n: f"Country #{n}")

    class Meta:
        model = models.Country


class ThemeFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Theme #{n}")

    class Meta:
        model = models.Theme


class UseCaseFactory(DjangoModelFactory):
    title = Sequence(lambda n: f"Use case #{n}")
    data_provider = Sequence(lambda n: f"Data Provider #{n}")
    data = Sequence(lambda n: f"Data #{n}")
    image = ImageField(color="blue")
    image_description = Sequence(lambda n: f"Image description #{n}")
    description = Sequence(lambda n: f"Description #{n}")
    copernicus_service = RelatedFactory(CopernicusServiceFactory)
    themes = RelatedFactory(ThemeFactory)
    country = SubFactory(CountryFactory)
    region = Sequence(lambda n: f"Region #{n}")
    locality = Sequence(lambda n: f"Locality #{n}")
    created_by = SubFactory(UserFactory)

    class Meta:
        model = models.UseCase


class ReferenceFactory(DjangoModelFactory):
    source = Sequence(lambda n: f"Theme #{n}")
    use_case = SubFactory(UseCaseFactory)
    date = Sequence(lambda n: f"Theme #{n}")

    class Meta:
        model = models.Reference
