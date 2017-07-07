from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.generic import FormView, RedirectView


class LoginView(FormView):
    success_url = '/'
    form_class = AuthenticationForm
    template_name = 'auth/login.html'

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
