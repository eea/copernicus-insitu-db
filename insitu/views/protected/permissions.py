from insitu.models import (
    CopernicusProvider,
    CountryProvider,
    DataProviderUser
)

class BasePermission(object):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated() and
                request.user.is_active)


class IsSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        return (super().has_permission(request, view)
                and request.user.is_superuser)


class IsCopernicusServiceProvider(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.service_resp
                return True
            except CopernicusProvider.DoesNotExist:
                return request.user.is_superuser
        return False


class IsCountryProvider(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.country_resp
                return True
            except CountryProvider.DoesNotExist:
                return request.user.is_superuser
        return False


class IsDataProviderUser(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.data_resp
                return True
            except DataProviderUser.DoesNotExist:
                return request.user.is_superuser
        return False

