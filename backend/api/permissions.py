from rest_framework import permissions
from . import models


class IsClubMemberReadOnlyPost(permissions.BasePermission):
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


class IsSelfOrReadOnlyUser(permissions.BasePermission):
    """
    Custom permission to only allow a user to update his/her details but see details of everyone.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow a user to edit his/her details
        return obj == request.user


class IsSecyOrRepOrReadOnlyClub(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative to write but allow everyone to read the details of a club.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow a secretary to delete
        elif request.method == 'DELETE':
            return request.user.has_perm("api.can_delete_club")
        # Only allow a secretary or club representative to update
        else:
            return request.user.has_perm('api.can_change_club') or \
                   models.ClubMembership.objects.filter(user__id=request.user.id,
                                                club_role__club=obj,
                                                club_role__privilege='REP').exists()


class IsRepClubRole(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to access a clubRole.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow the club representative
        return models.ClubMembership.objects.filter(user__id=request.user.id,
                                                club_role__club=obj.club,
                                                club_role__privilege='REP').exists()


class IsRepClubMembership(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to access a clubMembership.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow the club representative
        return models.ClubMembership.objects.filter(user__id=request.user.id,
                                                club_role__club=obj.club_role.club,
                                                club_role__privilege='REP').exists()
