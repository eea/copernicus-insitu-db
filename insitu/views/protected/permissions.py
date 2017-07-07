from insitu.models import CopernicusResponsible, CountryResponsible, DataProvider


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


class IsCopernicusServiceResponsible(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.service_resp
                return True
            except CopernicusResponsible.DoesNotExist:
                return False
        return False


class IsCountryResponsible(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.country_resp
                return True
            except CountryResponsible.DoesNotExist:
                return False
        return False


class IsDataProvider(IsAuthenticated):
    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            try:
                request.user.data_resp
                return True
            except DataProvider.DoesNotExist:
                return False
        return False