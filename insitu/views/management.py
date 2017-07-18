from django.urls import reverse_lazy

from insitu.views import protected
from insitu.views.protected.views import ProtectedTemplateView


class PicklistsManager(ProtectedTemplateView):
    template_name = 'picklists.html'
    permission_classes = (protected.IsSuperuser, )
    permission_denied_redirect = reverse_lazy('auth:login')
