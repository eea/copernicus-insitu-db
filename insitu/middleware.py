from sentry_sdk import configure_scope
from django.conf import settings


def sentry_middleware(get_response):
    def middleware(request):
        if settings.SENTRY_DSN:
            with configure_scope() as scope:
                scope.set_tag("site", settings.SENTRY_TAG_SITE)
                scope.set_tag("environment", settings.SENTRY_TAG_ENVIRONMENT)
                scope.set_tag("logger", "django")
                user = request.user
                if user.is_authenticated:
                    scope.user = {
                        "id": user.id,
                        "email": user.email,
                        "user": user.username,
                    }

        response = get_response(request)
        return response

    return middleware
