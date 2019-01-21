from django.conf import settings
from getenv import env

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