from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.views.generic import FormView, RedirectView

from insitu.models import User
from insitu.forms import TeamForm
from insitu.views.protected import (
    IsAuthenticated,
    ProtectedFormView,
    ProtectedUpdateView,
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
    permission_classes = (IsAuthenticated,)
    permission_denied_redirect = reverse_lazy('auth:login')
    model = User

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(EditTeamMatesView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
