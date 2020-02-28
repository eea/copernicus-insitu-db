from getenv import env
from django.conf import settings

def base(request):
    return {
        'DEBUG': settings.DEBUG,
        'READ_ONLY_GROUP': settings.READ_ONLY_GROUP,
        'PRODUCT_EDITOR_GROUP': settings.PRODUCT_EDITOR_GROUP,
        'PICKLISTS_EDITOR_GROUP': settings.PICKLISTS_EDITOR_GROUP
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
        'sentry_dsn': env('SENTRY_DSN', ''),
        'sentry_tag_server_name': request.get_host(),
        'sentry_tag_environment': settings.SENTRY_TAG_ENVIRONMENT,
        'sentry_tag_release': settings.SENTRY_TAG_RELEASE,
        'sentry_tag_site': settings.SENTRY_TAG_SITE,
    }
