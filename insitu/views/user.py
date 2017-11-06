from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView, RedirectView


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


class ChangePasswordView(FormView):
    success_url = '/'
    template_name = 'auth/change_password.html'
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
