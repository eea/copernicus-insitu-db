from django.shortcuts import get_object_or_404
from insitu.models import User
from copernicus.settings import PRODUCT_EDITOR_GROUP, READ_ONLY_GROUP


class BasePermission(object):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsDraftObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            super().has_object_permission(request, view, obj) and obj.state == "draft"
        )


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_active
        )


class IsNotReadOnlyUser(IsAuthenticated):
    def has_permission(self, request, view):
        return not request.user.groups.filter(name=READ_ONLY_GROUP).exists()


class IsSuperuser(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


class IsProductEditorUser(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.groups.filter(name=PRODUCT_EDITOR_GROUP).exists()
        )


class IsProductEditorUserOrIsSuperUser(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.groups.filter(name=PRODUCT_EDITOR_GROUP).exists()
            or request.user.is_superuser
        )


class IsOwnerUser(IsAuthenticated):
    def user_has_permission_over_object_or_related_objects(self, request, view, obj):
        pass

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and (
            obj.created_by == request.user
            or request.user.is_superuser
            or obj.has_user_perm(request.user)
            or request.user in obj.created_by.team.teammates.all()
        )


class IsRequestedUser(IsAuthenticated):
    def has_permission(self, request, view):
        requesting_user = get_object_or_404(User, id=view.kwargs["sender_user"])
        return (
            super().has_permission(request, view)
            and requesting_user.team.requests.filter(id=request.user.id).first()
        )


class IsCurrentUser(IsAuthenticated):
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk", None)
        if pk:
            requesting_user = get_object_or_404(User, id=pk)
        else:
            requesting_user = request.user
        return (
            super().has_permission(request, view)
            and requesting_user.id == request.user.id
        )
