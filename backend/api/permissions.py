"""
This module declares the custom Permission classes.
"""

from rest_framework import permissions
from . import models


class PostPermission(permissions.BasePermission):
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


class ConversationPermission(permissions.BasePermission):
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


class UserPermission(permissions.BasePermission):
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


class ClubPermission(permissions.BasePermission):
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


class ClubRolePermission(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to edit a clubRole
    and only allow club members to see a clubRole.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Only allow the club members to view
            return obj.club.has_member(request.user)

        # Only allow the club representative to edit
        return obj.club.has_rep(request.user)


class ClubMembershipPermission(permissions.BasePermission):
    """
    Custom permission to only allow the club representative to edit a
    clubMembership and only allow club members to see details of a
    clubMembership.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.club_role.club.has_member(request.user)

        # Only allow the club representative to edit
        return obj.club_role.club.has_rep(request.user)


class FeedbackPermission(permissions.BasePermission):
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


class FeedbackReplyPermission(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club representative
    or author to read the details of a feedbackReply.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.parent.author == request.user \
                    or request.user.is_secretary() \
                    or obj.parent.club.has_rep(request.user)

        # Do not allow anyone to modify or delete
        return False


class ProjectPermission(permissions.BasePermission):
    """
    Custom permission to only allow a secretary or the club members to read
    the details of a project. Also, to allow a club representative to update
    the details of a project.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_secretary() or \
                    obj.has_club_member(request.user)
        # Allow write permissions to only the club representative
        return obj.has_club_rep(request.user)


class ProjectMembershipPermission(permissions.BasePermission):
    """
    Custom permission to only allow the club representative and project leaders
    to delete a ProjectMembership and only allow club members to see details
    of a ProjectMembership.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Only allow the members of parent clubs to view details.
            return obj.project.has_club_member(request.user)

        if request.method == 'DELETE':
            # Only allow the leader and rep of parent clubs to delete.
            return obj.project.has_leader(request.user) or \
                obj.project.has_club_rep(request.user)

        # Do not allow anyone to edit
        return False


class ClubMembershipRequestPermission(permissions.BasePermission):
    """
    Custom permission for ClubMembershipRequest that only allows:
        1. Users to see their request
        2. Club representatives to see requests for their club
    """

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            # Do not allow anyone to modify/delete
            return False

        # Only allow access to the requester or the representative of the club
        # for which the request is made
        if obj.club.has_rep(request.user) or \
           obj.user == request.user:
            return True
        return False
