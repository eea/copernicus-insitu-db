# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PicklistsConfig(AppConfig):
    name = "picklists"
    verbose_name = "Picklists"

    class Meta:
        app_label = "picklists"
