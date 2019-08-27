from django import template
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from insitu.models import Product, Requirement, Data, DataProvider

register = template.Library()


@register.simple_tag
def get_product_number():
    return Product.objects.all().count()


@register.simple_tag
def get_requirement_number():
    return Requirement.objects.all().count()


@register.simple_tag
def get_data_number():
    return Data.objects.all().count()


@register.simple_tag
def get_data_provider_number():
    return DataProvider.objects.all().count()


@register.simple_tag
def get_logged_users_number():
    return Session.objects.filter(expire_date__gte=timezone.now()).count()


@register.simple_tag
def get_registered_users_number():
    return User.objects.all().count()
