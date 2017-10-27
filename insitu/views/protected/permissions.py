class BasePermission(object):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsDraftObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (super().has_object_permission(request, view, obj) and
                obj.state.name == 'draft')


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (request.user and
                request.user.is_authenticated() and
                request.user.is_active)


class IsSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        return (super().has_permission(request, view)
                and request.user.is_superuser)


class IsOwnerUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (super().has_object_permission(request, view, obj)
                and (obj.created_by == request.user or request.user.is_superuser))
