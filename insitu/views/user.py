from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect, HttpResponse
from django.views.generic import FormView, RedirectView

from insitu.models import User
from insitu.forms import TeamForm
from insitu.views.protected import (
    IsAuthenticated,
    IsNotReadOnlyUser,
    IsRequestedUser,
    ProtectedFormView,
    ProtectedUpdateView,
    ProtectedView,
    ProtectedTemplateView,
)


class LoginView(FormView):
    success_url = '/'
    form_class = AuthenticationForm
    template_name = 'auth/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('home'))
        return super(FormView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home')


class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class ChangePasswordView(ProtectedFormView):
    success_url = '/'
    template_name = 'auth/change_password.html'
    form_class = PasswordChangeForm
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class EditTeamMatesView(ProtectedUpdateView):
    success_url = '/'
    template_name = 'auth/edit_teammates.html'
    form_class = TeamForm
    context_object_name = 'user'
    permission_classes = (IsAuthenticated, IsNotReadOnlyUser)
    permission_denied_redirect = reverse_lazy('auth:login')
    model = User

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(EditTeamMatesView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class DeleteTeammateView(ProtectedTemplateView):
    permission_classes = (IsAuthenticated, )
    template_name = 'auth/delete_teammate.html'

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:edit_teammates')
        return super().permission_denied(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teammate'] = User.objects.get(id=self.kwargs['teammate_id'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'The teammate relation was removed!')
        return reverse('auth:edit_teammates')

    def post(self, request, *args, **kwargs):
        requesting_user = User.objects.get(id=kwargs['teammate_id'])
        if not request.user in requesting_user.team.teammates.all():
            return self.permission_denied(request)
        requesting_user.team.teammates.remove(request.user)
        request.user.team.teammates.remove(requesting_user)
        return redirect(self.get_success_url())



class AcceptTeammateRequestView(ProtectedView):
    permission_classes = (IsAuthenticated, IsRequestedUser)

    def permission_denied(self, request):
        self.permission_denied_redirect = reverse('auth:edit_teammates')
        return super().permission_denied(request)

    def get(self, request, *args, **kwargs):
        requesting_user = User.objects.get(id=kwargs['sender_user'])
        receiver_user = request.user
        requesting_user.team.requests.remove(receiver_user)
        receiver_user.team.requests.remove(requesting_user)
        receiver_user.team.teammates.add(requesting_user)
        requesting_user.team.teammates.add(receiver_user)
        requesting_user.save()
        receiver_user.save()
        messages.success(
            self.request,
            'You and {} {} are now teammates.'.format(
                requesting_user.first_name, requesting_user.last_name)
        )
        return redirect(reverse('auth:edit_teammates'))
