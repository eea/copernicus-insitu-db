from django.conf import settings
from getenv import env


def google_analytics(request):
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    ga_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', False)
    if not settings.DEBUG and ga_prop_id:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': ga_prop_id,
            'GOOGLE_ANALYTICS_DOMAIN': ga_domain,
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