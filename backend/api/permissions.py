from rest_framework import permissions
from . import models


class IsClubMemberReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow members of a club to read objects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to requests by members of club
        if request.method in permissions.SAFE_METHODS:
            if models.ClubMembership.objects.filter(user__id=request.user.id, club_role__club=obj.channel.club).exists():
                return True

        # Write permissions are only allowed to the owner of the snippet.
        return False


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow a user to update his/her details but see details of everyone.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
                return True

        # Only allow a user to edit his/her details
        return obj == request.user
