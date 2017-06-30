from django.views.generic import TemplateView, DetailView

from insitu import documents
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView
from picklists import models as pickmodels


class RequirementDetail(DetailView):
    template_name = 'requirement/detail.html'
    model = models.Requirement
    context_object_name = 'requirement'


class RequirementList(TemplateView):
    template_name = 'requirement/list.html'

    def get_context_data(self):
        context = super(RequirementList, self).get_context_data()
        disseminations = get_choices('name', model_cls=pickmodels.Dissemination)
        qualities = get_choices('name', model_cls=pickmodels.Quality)
        context.update({
            'disseminations': disseminations,
            'qualities': qualities,
        })
        return context


class RequirementListJson(ESDatatableView):
    columns = ['name', 'dissemination', 'quality']
    order_columns = columns
    filters = ['dissemination', 'quality']
    document = documents.RequirementDoc
