from . import models
from rest_framework import filters as rest_framework_filters
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .permissions import is_secretary


class MyClubsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        only_my_clubs = bool(request.query_params.get('my_clubs', None))
        if only_my_clubs:
            queryset = queryset.filter(roles__members__id__contains=request.user.id)
        return queryset


class MyClubRolesFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows club members to see club roles of their clubs.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(
            club__roles__members__id__contains=request.user.id,
        )
        return queryset


class MyClubMembershipsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows club members to see club roles of their clubs.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(
            club_role__club__roles__members__id__contains=request.user.id,
        )
        return queryset


class MyClubFeedbacksFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see feedbacks for clubs that they are representative of
    Secretaries to see all the feedbacks
    Users to see the feedbacks posted by them
    """

    def filter_queryset(self, request, queryset, view):
        club_id = int(request.query_params.get('club_id', -1))

        # Allow secretary to view feedbacks for all or selected clubs
        if is_secretary(request.user):
            if club_id != -1:
                queryset = queryset.filter(club__id=club_id)
        # Allow club representatives to only view feedbacks for their clubs
        else:
            if club_id != -1:
                # Allow to see all feedbacks only if user is representative of this club
                if models.ClubMembership.objects.filter(user__id=request.user.id,
                                                        club_role__club__id=club_id,
                                                        club_role__privilege='REP').exists():
                    queryset = queryset.filter(club__id=club_id)
                # Otherwise only show feedbacks posted by the user
                else:
                    queryset = queryset.filter(club__id=club_id, author=request.user)
            # Filter feedbacks of all clubs for which the user is representative
            # or the feedbacks which have been posted by the user
            else:
                club_list = models.Club.objects.filter(
                    roles__privilege='REP',
                    roles__members__id__contains=request.user.id
                )
                queryset = queryset.filter(Q(club__in=club_list) | Q(author=request.user))
        return queryset


class MyProjectsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see projects of clubs that they are member of
    Secretaries to see projects of all clubs or a selected club 
    """

    def filter_queryset(self, request, queryset, view):
        club_id = int(request.query_params.get('club_id', -1))

        # Allow secretary to view projects of all clubs or a selected club
        if is_secretary(request.user):
            if club_id != -1:
                queryset = queryset.filter(clubs__id__contains=club_id)
        # Allow club members to only view projects of their clubs
        else:
            if club_id != -1:
                # Allow to see all projects only if user is member of this club
                if models.ClubMembership.objects.filter(user__id=request.user.id,
                                                        club_role__club__id=club_id).exists():
                    queryset = queryset.filter(clubs__id__contains=club_id)
                # Otherwise raise PermissionDenied exception
                else:
                    raise PermissionDenied
            # Filter projects of all clubs for which the user is a member
            else:
                queryset = queryset.filter(clubs__roles__members__id__contains=request.user.id)
        return queryset


class MyPostsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see posts by channels that they have subscribed or of a selected channel
    """

    def filter_queryset(self, request, queryset, view):
        channel_id = int(request.query_params.get('channel_id', -1))

        if channel_id != -1:
            # Filter all posts by the specified channel
            queryset = queryset.filter(channel__id=channel_id)
        # Filter posts by the channel subscribed by the user
        else:
            queryset = queryset.filter(channel__subscribers__id__contains=request.user.id)
        return queryset
