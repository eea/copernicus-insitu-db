from django.contrib.sitemaps import Sitemap
from .models import (
    Product,
    Requirement,
    Data,
    DataProvider,
    Release,
)
from django.urls import reverse


class ProductSitemap(Sitemap):

    def items(self):
        return Product.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_detail_link()


class RequirementSitemap(Sitemap):

    def items(self):
        return Requirement.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_detail_link()


class DataSitemap(Sitemap):

    def items(self):
        return Data.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_detail_link()


class DataProviderSitemap(Sitemap):

    def items(self):
        return DataProvider.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_detail_link()


class AboutSitemap(Sitemap):

    def items(self):
        return [
            "about",
        ]

    def lastmod(self, obj):
        return Release.objects.latest("created_at").created_at

    def location(self, obj):
        return reverse("about")


class HelpSitemap(Sitemap):

    def items(self):
        return [
            "help",
        ]

    def location(self, obj):
        return reverse("help")


class ProductListSitemap(Sitemap):
    def items(self):
        return ["product_list"]

    def lastmod(self, page):
        return Product.objects.latest("updated_at").updated_at

    def location(self, page):
        return reverse("product:list")


class RequirementListSitemap(Sitemap):
    def items(self):
        return ["requirement_list"]

    def lastmod(self, page):
        return Requirement.objects.latest("updated_at").updated_at

    def location(self, page):
        return reverse("requirement:list")


class DataListSitemap(Sitemap):
    def items(self):
        return ["data_list"]

    def lastmod(self, page):
        return Data.objects.latest("updated_at").updated_at

    def location(self, page):
        return reverse("data:list")


class DataProviderListSitemap(Sitemap):
    def items(self):
        return ["provider_list"]

    def lastmod(self, page):
        return DataProvider.objects.latest("updated_at").updated_at

    def location(self, page):
        return reverse("provider:list")


class DocsSitemap(Sitemap):
    def items(self):
        return ["docs"]

    def location(self, page):
        return "/docs/guide.html"


class ReportsSitemap(Sitemap):
    def items(self):
        return ["reports"]

    def location(self, page):
        return "/reports/list"
