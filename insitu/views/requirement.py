from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from xworkflows import ForbiddenTransition

from insitu import documents
from insitu import forms
from insitu import models
from insitu.utils import get_choices
from insitu.views.base import ESDatatableView, CreatedByMixin
from insitu.views.protected import (
    LoggingProtectedTemplateView, LoggingProtectedDetailView,
    LoggingProtectedUpdateView, LoggingProtectedCreateView,
    LoggingProtectedDeleteView, LoggingTransitionProtectedDetailView)
from picklists import models as pickmodels
from insitu.views.protected.permissions import (
    IsAuthenticated,
    IsOwnerUser,
    IsDraftObject
)


class GetInitialMixin:

    def get_requirement(self):
        try:
            return self.get_object()
        except AttributeError:
            pk = self.request.GET.get('pk', None)
            try:
                return models.Requirement.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return

    def get_initial(self):
        requirement = self.get_requirement()
        if not requirement:
            return super().get_initial()

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


class RequirementDetail(LoggingProtectedDetailView):
    template_name = 'requirement/detail.html'
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsAuthenticated,)
    target_type = 'requirement'

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:login')
        return super().permission_denied(request)


class RequirementList(LoggingProtectedTemplateView):
    template_name = 'requirement/list.html'
    permission_classes = (IsAuthenticated, )
    target_type = 'requirements'

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
               'horizontal_resolution', 'vertical_resolution', 'state']
    order_columns = columns
    filters = ['dissemination', 'quality_control_procedure', 'group']
    document = documents.RequirementDoc
    permission_classes = (IsAuthenticated, )


class RequirementAdd(GetInitialMixin, CreatedByMixin,
                     LoggingProtectedCreateView):
    template_name = 'requirement/add.html'
    model = models.Requirement
    permission_classes = (IsAuthenticated, )
    target_type = 'requirement'

    def get_form_class(self):
        requirement = self.get_requirement()
        if requirement:
            self.post_action = 'cloned requirement {pk} to'.format(
                pk=requirement.pk)
            self.post_action_failed = 'tried to clone object {pk} of'.format(
                pk=requirement.pk
            )
            return forms.RequirementCloneForm
        return forms.RequirementForm

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.object
        return reverse('requirement:detail', kwargs={'pk': instance.pk})


class RequirementEdit(GetInitialMixin, LoggingProtectedUpdateView):
    template_name = 'requirement/edit.html'
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsOwnerUser, IsDraftObject)
    target_type = 'requirement'

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        instance = self.get_object()
        return reverse('requirement:detail',
                       kwargs={'pk': instance.pk})


class RequirementDelete(LoggingProtectedDeleteView):

    template_name = 'requirement/delete.html'
    form_class = forms.RequirementForm
    model = models.Requirement
    context_object_name = 'requirement'
    permission_classes = (IsOwnerUser, IsDraftObject)
    target_type = 'requirement'

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('requirement:list')
        return super().permission_denied(request)

    def get_success_url(self):
        return reverse('requirement:list')


class RequirementTransition(LoggingTransitionProtectedDetailView):
    model = models.Requirement
    template_name = 'requirement/transition.html'
    permission_classes = (IsAuthenticated, )
    context_object_name = 'requirement'
    target_type = 'requirement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.kwargs.get('source')
        target = self.kwargs.get('target')
        transition = models.ValidationWorkflow.get_transition(source, target)
        if not transition:
            raise Http404()
        context.update({
            'target': target,
            'source': source,
            'objects': [
                {
                    'obj': item,
                    'type': item.__class__.__name__
                }
                for item in self.object.get_related_objects()
            ]
        })
        return context

    def post(self, request, *args, **kwargs):
        requirement = self.get_object(self.get_queryset())
        source = self.kwargs.get('source')
        target = self.kwargs.get('target')
        self.post_action = 'changed state from {source} to {target} for'.format(
            source=source,
            target=target
        )
        id = self.get_object_id()
        self.log_action(request, self.post_action, id)
        try:
            transition_name = models.ValidationWorkflow.get_transition(source, target)
            transition = getattr(requirement, transition_name)
            requirement.requesting_user = self.request.user
            if transition.is_available():
                transition()
                return HttpResponseRedirect(reverse('requirement:detail',
                                                    kwargs={'pk': requirement.pk}))
        except ForbiddenTransition:
            pass
        raise Http404()
