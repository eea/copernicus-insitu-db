from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, TemplateView

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

    def get_success_url(self, id):
        return reverse('requirement:detail', kwargs={'pk': id})

    def _create_metric(self, threshold, breakthrough, goal):
        return models.Metric.objects.create(
            threshold=threshold,
            breakthrough=breakthrough,
            goal=goal
        )
    
    def post(self, request, *args, **kwargs):
        form =  self.get_form()
        if form.is_valid():
            data = form.data
            uncertainty = self._create_metric(
                data['uncertainty_threshold'], 
                data['uncertainty_breakthrough'],
                data['uncertainty_goal'],
            )
            frequency =  self._create_metric(
                data['frequency_threshold'], 
                data['frequency_breakthrough'],
                data['frequency_goal'],
            )
            timeliness =  self._create_metric(
                data['timeliness_threshold'], 
                data['timeliness_breakthrough'],
                data['timeliness_goal'],
            )
            horizontal_resolution =  self._create_metric(
                data['horizontal_resolution_threshold'], 
                data['horizontal_resolution_breakthrough'],
                data['horizontal_resolution_goal'],
            )
            vertical_resolution =  self._create_metric(
                data['vertical_resolution_threshold'], 
                data['vertical_resolution_breakthrough'],
                data['vertical_resolution_goal'],
            )
            dissemination = pickmodels.Dissemination.objects.get(
                id=data['dissemination']
            )
            quality = pickmodels.Quality.objects.get(id=data['quality'])
            requirement = models.Requirement.objects.create(
                name=data['name'],
                note=data['note'],
                dissemination=dissemination,
                quality=quality,
                uncertainty=uncertainty,
                frequency=frequency,
                timeliness=timeliness,
                horizontal_resolution=horizontal_resolution,
                vertical_resolution=vertical_resolution
            )
            return redirect(self.get_success_url(requirement.id))
        else:
            return super().post(self, request, *args, **kwargs)

