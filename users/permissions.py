from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.roles.filter(name='admin').exists()

class IsCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.roles.filter(name='creator').exists()

class IsPollOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For poll options
        return obj.poll.user == request.user or request.user.roles.filter(name='admin').exists()