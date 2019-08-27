from getenv import env
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from insitu.models import Product, Requirement, Data, DataProvider


def base(request):
    return {
        'DEBUG': settings.DEBUG,
        'READ_ONLY_GROUP': settings.READ_ONLY_GROUP
    }


def matomo(request):
    matomo = getattr(settings, 'MATOMO', False)
    if not settings.DEBUG and matomo:
        return {
            'MATOMO': matomo,
        }
    return {}


def crazy_egg(request):
    crazy_egg_path = getattr(settings, 'CRAZY_EGG', '')
    if not settings.DEBUG and crazy_egg_path:
        return {
            'CRAZY_EGG': crazy_egg_path
        }
    return {}


def sentry(request):
    sentry_id = ''
    if hasattr(request, 'sentry'):
        sentry_id = request.sentry['id']
    return {
        'sentry_id': sentry_id,
        'sentry_public_id': env('SENTRY_PUBLIC_DSN', ''),
    }


def statistics(request):
    return {
        'products': Product.objects.all().count(),
        'requirements': Requirement.objects.all().count(),
        'data': Data.objects.all().count(),
        'data_providers': DataProvider.objects.all().count(),
        'logged_users': Session.objects.filter(expire_date__gte=timezone.now()).count(),
        'registered_users': User.objects.all().count(),
    }
