from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, TemplateView

from django.core.urlresolvers import reverse
from django.views.generic import DetailView
from django.views.generic import UpdateView

from insitu import documents
from insitu import forms
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


class RequirementAdd(CreateView):
    template_name = 'requirement/add.html'
    form_class = forms.RequirementForm
    model = models.Requirement

    def get_success_url(self):
        instance = self.object
        return reverse('requirement:detail', kwargs={'pk': instance.pk})


class RequirementEdit(UpdateView):
    template_name = 'requirement/edit.html'
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = 'requirement'

    def get_initial(self):
        requirement = self.get_object()
        initial_data = super().get_initial()
        for field in ['name', 'note', 'dissemination', 'quality']:
            initial_data[field] = getattr(requirement, field)
        for field in ['uncertainty', 'frequency', 'timeliness',
                      'horizontal_resolution', 'vertical_resolution']:
            for attr in ['threshold', 'breakthrough', 'goal']:
                initial_data["_".join([field, attr])] = getattr(getattr(requirement,
                                                                        field), attr)
        return initial_data.copy()

    def get_success_url(self):
        instance = self.get_object()
        return reverse('requirement:detail',
                       kwargs={'pk': instance.pk})
