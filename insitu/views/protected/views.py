import warnings
from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    FormView,
    FormMixin,
    UpdateView,
    DeleteView,
    CreateView,
)
from django.views.generic.list import ListView
from insitu.views.action_logging.base_logging import (
    ListLoggingView,
    UpdateLoggingView,
    CreateLoggingView,
    DeleteLoggingView,
    DetailLoggingView,
    TrasitionLoggingView,
)


class ProtectedViewBase(type):
    def __new__(cls, name, bases, attrs):
        try:
            dispatcher = attrs.pop("dispatch")
        except KeyError:
            dispatcher = next(
                base.dispatch for base in bases if hasattr(base, "dispatch")
            )
        try:
            dispatcher._checks_permissions
        except AttributeError:
            dispatcher = cls._permission_wrapper(dispatcher)
            dispatcher._checks_permissions = None
        attrs["dispatch"] = dispatcher
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def _permission_wrapper(dispatch):
        @wraps(dispatch)
        def wrapper(self, request, *args, **kwargs):
            permissions_checked = getattr(self, "_permissions_checked", False)
            if not permissions_checked:
                self._permissions_checked = True
            if permissions_checked or self.check_permissions(request):
                return dispatch(self, request, *args, **kwargs)
            else:
                return self.permission_denied(request)

        return wrapper


class ProtectedView(View, metaclass=ProtectedViewBase):
    """
    A view that checks all its `permission_classes`' `has_permission()` method.
    """

    # don't change this class's name, it's hardcoded in the metaclass

    permission_classes = ()
    permission_denied_redirect = None

    def get_permissions(self):
        try:
            self.__permissions
        except AttributeError:
            self.__permissions = [
                permission() for permission in self.permission_classes
            ]
            if not self.__permissions:
                warnings.warn(
                    "View %s " "has empty permissions." % type(self).__name__,
                    stacklevel=2,
                )

        return self.__permissions

    def check_permissions(self, request):
        return all(
            permission.has_permission(request, self)
            for permission in self.get_permissions()
        )

    def permission_denied(self, request):
        if self.permission_denied_redirect:
            return redirect(self.permission_denied_redirect)
        return HttpResponseForbidden()


class ProtectedObjectMixin(object):
    """
    A mixin running permissions' `has_object_permission()` against views
    with a `get_object()` method.
    """

    def check_permissions(self, request):
        if not super().check_permissions(request):
            return False

        obj = self.get_object()
        return all(
            permission.has_object_permission(request, self, obj)
            for permission in self.get_permissions()
        )


class ProtectedDetailView(ProtectedObjectMixin, ProtectedView, DetailView):
    """
    Convenience view adding permissions support to
    `django.views.generic.DetailView`.
    """

    pass


class LoggingProtectedDetailView(
    DetailLoggingView, ProtectedObjectMixin, ProtectedView, DetailView
):
    """
    Convenience view adding permissions and logging
    support to `django.views.generic.DetailView`.
    """

    pass


class LoggingTransitionProtectedDetailView(TrasitionLoggingView, ProtectedDetailView):
    """
    Convenience view adding permissions and logging
    support for transition view.
    """

    pass


class ProtectedListView(ProtectedView, ListView):
    """
    Convenience view adding permissions support to
    `django.views.generic.ListView`.
    """

    pass


class ProtectedTemplateView(ProtectedView, TemplateView):

    """
    Convenience view adding permissions support to
    `django.views.generic.TemplateView`.
    """

    pass


class LoggingProtectedTemplateView(ListLoggingView, ProtectedView, TemplateView):
    """
    Convenience view adding permissions and logging
     support to `django.views.generic.TemplateView`.
    """

    pass


class ProtectedFormViewBase(FormMixin, ProtectedViewBase):
    pass


class ProtectedFormView(ProtectedView, FormView, metaclass=ProtectedFormViewBase):
    """
    Convenience view adding permissions support to
    `django.views.generic.FormView`.
    """

    pass


class ProtectedCreateView(ProtectedView, CreateView, metaclass=ProtectedFormViewBase):
    """
    Convenience view adding permissions support to
    `django.views.generic.CreateView`.
    """

    pass


class LoggingProtectedCreateView(
    CreateLoggingView, ProtectedView, CreateView, metaclass=ProtectedFormViewBase
):
    """
    Convenience view adding permissions and logging
    support to `django.views.generic.CreateView`.
    """

    pass


class ProtectedUpdateView(
    ProtectedObjectMixin, ProtectedView, UpdateView, metaclass=ProtectedFormViewBase
):
    """
    Convenience view adding permissions support to
    `django.views.generic.UpdateView`.
    """

    pass


class LoggingProtectedUpdateView(
    UpdateLoggingView,
    ProtectedObjectMixin,
    ProtectedView,
    UpdateView,
    metaclass=ProtectedFormViewBase,
):
    """
    Convenience view adding permissions and logging
    support to `django.views.generic.UpdateView`.
    """

    pass


class ProtectedDeleteView(
    ProtectedObjectMixin, ProtectedView, DeleteView, metaclass=ProtectedFormViewBase
):

    """
    Convenience view adding permissions support to
    `django.views.generic.DeleteView`.
    """

    pass


class LoggingProtectedDeleteView(
    DeleteLoggingView,
    ProtectedObjectMixin,
    ProtectedView,
    DeleteView,
    metaclass=ProtectedFormViewBase,
):

    """
    Convenience view adding permissions and logging
    support to `django.views.generic.DeleteView`.
    """

    pass
