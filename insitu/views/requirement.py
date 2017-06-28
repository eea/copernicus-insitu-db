from django.views.generic import DetailView

from insitu import models


class RequirementDetail(DetailView):
    template_name = 'requirement/detail.html'
    model = models.Requirement
    context_object_name = 'requirement'

