from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow Admins to access any task,
    but standard Users can only access their own tasks.
    """

    def has_permission(self, request, view):
        # Allow access only if the user is authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Return True if the user is an Admin OR the owner of the object.
        """
        # We check if the user is a Django Staff member OR belongs to the 'Admin' group.
        if request.user.is_staff or request.user.groups.filter(name='Admin').exists():
            return True

        # If not an Admin, the user must be the 'owner' of the task.
        return obj.owner == request.user