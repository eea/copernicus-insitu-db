class UseCaseIsEditable:
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return obj.state == "draft"


class UseCaseIsCreator:
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
