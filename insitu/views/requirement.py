from django.core.urlresolvers import reverse

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView
from insitu.views.protected import (
    ProtectedTemplateView, ProtectedDetailView,
    ProtectedUpdateView, ProtectedCreateView, ProtectedDeleteView)
from picklists import models as pickmodels
from insitu.views.protected.permissions import (
    IsAuthenticated,
    IsCopernicusServiceResponsible,
)

class GetInitialMixing(object):

    def get_initial(self):
        if self.get_object():
            requirement = self.get_object()
            initial_data = super().get_initial()
            for field in ['name', 'note', 'dissemination',
                          'quality_control_procedure', 'group']:
                initial_data[field] = getattr(requirement, field)
            for field in ['uncertainty', 'update_frequency', 'timeliness',
                          'horizontal_resolution', 'vertical_resolution']:
                for attr in ['threshold', 'breakthrough', 'goal']:
                    initial_data["_".join([field, attr])] = getattr(
                        getattr(requirement, field), attr
                    )
            return initial_data.copy()



class RequirementDetail(ProtectedDetailView):
    template_name = 'requirement/detail.html'
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsAuthenticated,)

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:login')
        return super().permission_denied(request)


class RequirementList(ProtectedTemplateView):
    template_name = 'requirement/list.html'
    permission_classes = (IsAuthenticated, )

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:login')
        return super().permission_denied(request)

    def get_context_data(self):
        context = super(RequirementList, self).get_context_data()
        disseminations = get_choices('name', model_cls=pickmodels.Dissemination)
        quality_control_procedures = get_choices(
            'name', model_cls=pickmodels.QualityControlProcedure
        )
        groups = get_choices('name', model_cls=pickmodels.RequirementGroup)
        context.update({
            'disseminations': disseminations,
            'quality_control_procedures': quality_control_procedures,
            'groups': groups,
        })
        return context


class RequirementListJson(ESDatatableView):
    columns = ['name', 'dissemination', 'quality_control_procedure', 'group',
               'uncertainty', 'update_frequency', 'timeliness',
               'horizontal_resolution', 'vertical_resolution']
    order_columns = columns
    filters = ['dissemination', 'quality_control_procedure', 'group']
    document = documents.RequirementDoc
    permission_classes = (IsAuthenticated, )


class RequirementAdd(GetInitialMixing, ProtectedCreateView):
    template_name = 'requirement/add.html'
    model = models.Requirement
    permission_classes = (IsCopernicusServiceResponsible,)

    def get_object(self):
        pk = self.request.GET.get('pk', '')
        if pk:
            object = models.Requirement.objects.filter(pk=pk).first()
            if object:
                return object

    def get_form_class(self):
        requirement = self.get_object()
        if requirement:
            return forms.RequirementCloneForm

        return forms.RequirementForm

    def get_initial(self):
        if self.get_object():
            return super().get_initial()

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.object
        return reverse('requirement:detail', kwargs={'pk': instance.pk})


class RequirementEdit(GetInitialMixing, ProtectedUpdateView):
    template_name = 'requirement/edit.html'
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsCopernicusServiceResponsible,)

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.get_object()
        return reverse('requirement:detail',
                       kwargs={'pk': instance.pk})


class RequirementDelete(ProtectedDeleteView):

    template_name = 'requirement/delete.html'
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsCopernicusServiceResponsible,)

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        return reverse('requirement:list')
