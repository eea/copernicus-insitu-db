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
from django.conf.urls import url, include, static
from django.contrib import admin
from django.conf import settings

handler500 = "insitu.views.errors.handler500"

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^hijack/", include("hijack.urls")),
    url(r"^", include("insitu.urls")),
    url(r"^use_cases/", include(("use_cases.urls", "use_cases"), namespace="use_cases")),
    url(r"^picklists/", include(("picklists.urls", "picklists"), namespace="pick")),
    url(r"^explorer/", include("explorer.urls")),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [
        url(r"^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
