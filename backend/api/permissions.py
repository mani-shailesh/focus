"""
This module declares the custom Permission classes.
"""

from rest_framework import permissions
from . import models


class IsRepOrReadOnlyPost(permissions.BasePermission):
    """
    Custom permission to allow everyone to read posts but only allow
    representative of a club to update or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the club representative.
        return obj.channel.club.has_rep(request.user)


class IsClubMemberReadOnlyConversation(permissions.BasePermission):
    """
    Custom permission to allow only club members to read conversations and do
    not allow anyone to write.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to only club members
        if request.method in permissions.SAFE_METHODS:
            return obj.channel.club.has_member(request.user)

        # Write permissions are denied to everyone.
        return False


class IsSelfOrReadOnlyUser(permissions.BasePermission):
    """
    Custom permission to only allow a user to update his/her details but see
    details of everyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow a user to edit his/her details
        return obj == request.user


class IsSecyOrRepOrReadOnlyClub(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative to
    write but allow everyone to read the details of a club.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow a secretary to delete
        if request.method == 'DELETE':
            return request.user.is_secretary()
        # Only allow a secretary or club representative to update
        return request.user.is_secretary() or \
            obj.has_rep(request.user)


class IsRepOrMemReadOnlyClubRole(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to edit a clubRole
    and only allow club members to view a clubRole.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.club.has_member(request.user)

        # Only allow the club representative to edit
        return obj.club.has_rep(request.user)


class IsRepOrMemReadOnlyClubMembership(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to edit a
    clubMembership.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow a club member to view details
        if request.method in permissions.SAFE_METHODS:
            return obj.club_role.club.has_member(request.user)

        # Only allow the club representative to edit
        return obj.club_role.club.has_rep(request.user)


class IsSecyOrRepOrAuthorFeedback(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative or
    author to read the details of a feedback.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.author == request.user \
                    or request.user.is_secretary() \
                    or obj.club.has_rep(request.user)
        # Do not allow write permissions to anyone
        return False


class IsSecyOrRepOrAuthorFeedbackReply(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative
    or author to read the details of a feedbackReply.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.parent.author == request.user \
                    or request.user.is_secretary() \
                    or obj.parent.club.has_rep(request.user)
        # Do not allow write permissions to anyone
        return False


class IsRepOrSecyAndClubMemberReadOnlyProject(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club members to read
    the details of a project. Also, to allow a club representative to update
    the details of a project.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_secretary() \
                    or models.ClubMembership.objects.filter(
                        user__id=request.user.id,
                        club_role__club__in=obj.clubs.all()
                    ).exists()
        # Allow write permissions to only the club representative
        return models.ClubMembership.objects.filter(
            user__id=request.user.id,
            club_role__club__in=obj.clubs.all(),
            club_role__privilege='REP'
        ).exists()
