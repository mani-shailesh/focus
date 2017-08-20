"""
Contains Filters for API endpoints to restrict the returned representation
based on the request.
"""

from rest_framework import filters as rest_framework_filters
from rest_framework.exceptions import ParseError
from django.db.models import Q

from . import models, constants


class ClubFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows users to see only their own objects, if requested.
    """

    def filter_queryset(self, request, queryset, view):
        only_my_clubs = bool(int(request.query_params.get('only_my', 0)))
        if only_my_clubs:
            queryset = queryset.filter(
                roles__members__id__contains=request.user.id)
        return queryset


class ClubMembershipRequestFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows a user to see her own requests or the requests for
    a club that she is a representative of. It also allows further filtering
    based on following parameters in request:
        1. club_id: Only show requests for provided club id
        2. only_my: Only show requests made by current user
        3. pending: Show all if unset, only pending if true, only not pending
        otherwise
        4. order:   Order most recently initiated first if set to -1 or unset,
        otherwise reverse the order
    """

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_requests = bool(int(
                request.query_params.get('only_my', 0)))
            pending = int(request.query_params.get('pending', -1))
        except:
            raise ParseError

        # Get the list of all clubs that user is a representative of
        club_list = models.Club.objects.filter(
            roles__privilege=constants.PRIVILEGE_REP,
            roles__members__id__contains=request.user.id
        )
        queryset = queryset.filter(
            Q(club__in=club_list) | Q(user=request.user)
        )

        if pending != -1:
            if pending:
                queryset = queryset.filter(
                    status=constants.REQUEST_STATUS_PENDING
                )
            else:
                queryset = queryset.exclude(
                    status=constants.REQUEST_STATUS_PENDING
                )

        if club_id != -1:
            queryset = queryset.filter(club__id=club_id)

        if only_my_requests:
            queryset = queryset.filter(user=request.user)

        if order == -1:
            queryset = queryset.order_by('-initiated')
        else:
            queryset = queryset.order_by('initiated')
        return queryset


class ClubRoleFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows club members to see club roles of their clubs.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(
            club__roles__members__id__contains=request.user.id,
        )
        return queryset


class ClubMembershipFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that only allows club members to see club roles of their clubs.
    """

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(
            club_role__club__roles__members__id__contains=request.user.id,
        )
        return queryset


class FeedbackFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
        1. Users to see feedbacks for clubs that they are representative of
        2. Secretaries to see all the feedbacks
        3. Users to see the feedbacks posted by them
    """

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_feedbacks = bool(int(
                request.query_params.get('only_my', 0)))
        except:
            raise ParseError

        # Allow secretary to view feedbacks for all or selected clubs
        if not request.user.is_secretary():
            # Filter feedbacks of all clubs for which the user
            # is representative or the feedbacks which have
            # been posted by the user
            club_list = models.Club.objects.filter(
                roles__privilege='REP',
                roles__members__id__contains=request.user.id
            )
            queryset = queryset.filter(
                Q(club__in=club_list) | Q(author=request.user))

        if club_id != -1:
            queryset = queryset.filter(club__id=club_id)

        if only_my_feedbacks:
            queryset = queryset.filter(author__id=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset


class ProjectFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see projects of clubs that they are member of
    Secretaries to see projects of all clubs or a selected club
    """

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            only_my_projects = bool(
                int(request.query_params.get('only_my', 0)))

        except:
            raise ParseError

        # Allow secretary to view projects of all clubs or a selected club
        # Allow club members to only view projects of their clubs
        if not request.user.is_secretary():
            # Filter projects of all clubs for which the user is a member
            queryset = queryset.filter(
                clubs__roles__members__id__contains=request.user.id)

        if club_id != -1:
            queryset = queryset.filter(clubs__id__contains=club_id)

        if only_my_projects:
            queryset = queryset.filter(members__id__contains=request.user.id)

        return queryset


class PostFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    1. Users to see posts by channels that they have subscribed
    or of a selected channel
    2. Impose an ascending or descending order on the posts
    as per their `created` attribute
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
            queryset = queryset.filter(
                channel__subscribers__id__contains=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset


class ConversationFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that:
    1. Restricts users to only see conversations on channels of a club that
    they are member of
    2. Impose an ascending or descending order on the conversations as per
    their `created` attribute
    """

    def filter_queryset(self, request, queryset, view):
        try:
            parent_id = int(request.query_params.get('parent_id', -1))
            channel_id = int(request.query_params.get('channel_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_conversations = bool(
                int(request.query_params.get('only_my', 0)))
            include_replies = bool(int(request.query_params.get('replies', 0)))
        except:
            raise ParseError

        # Filter conversations by the channel of clubs that the user is
        # a member of
        queryset = queryset.filter(
            channel__club__roles__members__id__contains=request.user.id)

        if parent_id != -1:
            queryset = queryset.filter(parent__id=parent_id)
            include_replies = True

        if channel_id != -1:
            queryset = queryset.filter(channel__id=channel_id)

        if not include_replies:
            queryset = queryset.filter(parent__isnull=True)

        if only_my_conversations:
            queryset = queryset.filter(author__id=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset


class ChannelFilter(rest_framework_filters.BaseFilterBackend):
    """
    Class to filter out the channels as per the request.
    """

    def filter_queryset(self, request, queryset, view):
        try:
            only_my_channels = bool(int(
                request.query_params.get('only_my', 0)))
            club_id = int(request.query_params.get('club_id', -1))
        except:
            raise ParseError

        if club_id != -1:
            queryset = queryset.filter(
                club__id=club_id
            )

        if only_my_channels:
            queryset = queryset.filter(
                subscribers__id__contains=request.user.id)

        return queryset


class FeedbackReplyFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    Users to see feedback replies for clubs that they are representative of
    Secretaries to see all the feedback replies
    Users to see the replies to feedbacks posted by them
    """

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_feedbacks = bool(int(
                request.query_params.get('only_my', 0)))
        except:
            raise ParseError

        # Allow secretary to view feedback replies for all or selected clubs
        if not request.user.is_secretary():
            # Filter feedback replies of all clubs for which the user
            # is representative or the replies to feedbacks which have
            # been posted by the user
            club_list = models.Club.objects.filter(
                roles__privilege='REP',
                roles__members__id__contains=request.user.id
            )
            queryset = queryset.filter(
                Q(parent__club__in=club_list) | Q(parent__author=request.user))

        if club_id != -1:
            queryset = queryset.filter(parent__club__id=club_id)

        if only_my_feedbacks:
            queryset = queryset.filter(parent__author__id=request.user.id)

        if order == -1:
            queryset = queryset.order_by('-created')
        else:
            queryset = queryset.order_by('created')

        return queryset
