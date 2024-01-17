"""copernicus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import include, path

from django.contrib import admin
from django.conf import settings

handler500 = "insitu.views.errors.handler500"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hijack/", include("hijack.urls")),
    path("", include("insitu.urls")),
    path("picklists/", include(("picklists.urls", "picklists"), namespace="pick")),
    path("explorer/", include("explorer.urls")),
    path("markdownx/", include("markdownx.urls")),
]

if settings.USE_CASES_FEATURE_TOGGLE:
    urlpatterns += [
        path(
            "use_cases/",
            include(("use_cases.urls", "use_cases"), namespace="use_cases"),
        )
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
