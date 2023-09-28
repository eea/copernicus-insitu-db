from django.core.management.base import BaseCommand
from insitu.models import CopernicusService as InsituCoopernicusService
from picklists.models import InspireTheme
from picklists.models import Country as InsituCountry
from use_cases.models import CopernicusService, Country, Theme


class Command(BaseCommand):
    help = "Clone picklists into use cases metadata models"

    def handle(self, *args, **options):
        original_copernicus_services = InsituCoopernicusService.objects.all()
        original_countries = InsituCountry.objects.all()
        original_themes = InspireTheme.objects.all()

        for original_copernicus_service in original_copernicus_services:
            copernicus_service, created = CopernicusService.objects.get_or_create(
                name=original_copernicus_service.name,
            )
            if created:
                print(f"Created copernicus service: {copernicus_service.name}")

        for original_country in original_countries:
            country, created = Country.objects.get_or_create(
                code=original_country.code,
                defaults={"name": original_country.name},
            )
            if created:
                print(f"Created country: {country.code}/ {country.name}")

        for original_theme in original_themes:
            theme, created = Theme.objects.get_or_create(
                name=original_theme.name,
            )
            if created:
                print(f"Created theme: {theme.name}")
