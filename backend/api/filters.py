from . import models
from rest_framework import filters as rest_framework_filters
from rest_framework.exceptions import PermissionDenied, ParseError
from django.db.models import Q
from .permissions import is_secretary


class MyClubsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        only_my_clubs = bool(int(request.query_params.get('only_my', 0)))
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
        try:
            club_id = int(request.query_params.get('club_id', -1))
        except:
            raise ParseError

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
        try:
            club_id = int(request.query_params.get('club_id', -1))
        except:
            raise ParseError

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
    Impose an ascending or descending order on the posts as per their `created` attribute
    """

    def filter_queryset(self, request, queryset, view):
        try:
            channel_id = int(request.query_params.get('channel_id', -1))
            order = int(request.query_params.get('order', -1))
        except:
            raise ParseError

        if channel_id != -1:
            # Filter all posts by the specified channel
            queryset = queryset.filter(channel__id=channel_id)
        # Filter posts by the channel subscribed by the user
        else:
            queryset = queryset.filter(channel__subscribers__id__contains=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset


class MyConversationsFilterBackend(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see conversations on channels of a club that they are member of
    Impose an ascending or descending order on the posts as per their `created` attribute
    """

    def filter_queryset(self, request, queryset, view):
        try:
            channel_id = int(request.query_params.get('channel_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_conversations = bool(int(request.query_params.get('only_my', 0)))
            include_replies = bool(int(request.query_params.get('replies', 0)))
        except:
            raise ParseError

        if channel_id != -1:
            # Allow to see conversations only if user is a member of this club
            if models.ClubMembership.objects.filter(user__id=request.user.id,
                                                    club_role__club__channel__id=channel_id).exists():
                queryset = queryset.filter(channel__id=channel_id)
            # Otherwise raise PermissionDenied exception
            else:
                raise PermissionDenied
        else:
            # Filter conversations by the channel of clubs that the user is a member of
            queryset = queryset.filter(channel__club__roles__members__id__contains=request.user.id)

        if not include_replies:
            queryset = queryset.filter(parent__isnull=True)

        if only_my_conversations:
            queryset = queryset.filter(author__id=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset
