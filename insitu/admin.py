# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from insitu import models


admin.site.register(models.CopernicusService)
admin.site.register(models.EntrustedEntity)
admin.site.register(models.Component)
admin.site.register(models.Requirement)
admin.site.register(models.Product)
admin.site.register(models.ProductRequirement)
admin.site.register(models.DataResponsible)
admin.site.register(models.DataResponsibleDetails)
admin.site.register(models.DataGroup)
admin.site.register(models.DataRequirement)
admin.site.register(models.DataResponsibleRelation)
