"""
Contains Filters for API endpoints to restrict the returned representation
based on the request.
"""

import coreapi

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

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only Clubs that the current user'
                                      + ' is a member of, if set to non-zero value.',
                          type='integer'),
        ]


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

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return requests for this Club',
                          type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only requests made by current'
                                      + ' user if set to a non-zero value.',
                          type='integer'),
            coreapi.Field(name='pending', location='query', required=False,
                          description='Return all if unset or set to -1, only'
                                      + ' not pending if 0, only pending otherwise',
                          type='integer'),
            coreapi.Field(name='order', location='query', required=False,
                          description='Order most recently initiated request'
                                      + ' first if set to -1 or unset, otherwise reverse the'
                                      + ' order', type='integer'),
        ]

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
    Filter that only allows:
        1. Users to see roles in only their clubs by default.
        2. Users to see roles in a specific club based on request, if they are
        a member of that club.
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return roles for this Club',
                          type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
        except:
            raise ParseError
        queryset = queryset.filter(
            club__roles__members__id__contains=request.user.id
        )
        if club_id != -1:
            queryset = queryset.filter(club__id=club_id)
        return queryset


class ClubMembershipFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
        1. Users to see members of all clubs by default
        2. Users to see members of a specific club based on request
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return members for this Club',
                          type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
        except:
            raise ParseError
        if club_id != -1:
            queryset = queryset.filter(club_role__club__id=club_id)
        return queryset


class FeedbackFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
        1. Users to see feedbacks for clubs that they are representative of
        2. Secretaries to see all the feedbacks
        3. Users to see the feedbacks posted by them
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return feedbacks for this Club',
                          type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only feedbacks posted by current'
                                      + ' user if set to a non-zero value.',
                          type='integer'),
            coreapi.Field(name='order', location='query', required=False,
                          description='Order most recently posted feedback'
                                      + ' first if set to -1 or unset, otherwise reverse the'
                                      + ' order', type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_feedbacks = bool(int(
                request.query_params.get('only_my', 0)))
        except:
            raise ParseError

        # Allow secretary to view feedbacks for all or selected clubs
        if not request.user.is_secretary:
            # Filter feedbacks of all clubs for which the user
            # is representative or the feedbacks which have
            # been posted by the user
            club_list = models.Club.objects.filter(
                roles__privilege=constants.PRIVILEGE_REP,
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

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return projects for this Club',
                          type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only projects that this User is'
                                      + ' a member of, if set to a non-zero value.',
                          type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            only_my_projects = bool(
                int(request.query_params.get('only_my', 0)))

        except:
            raise ParseError

        # Allow secretary to view projects of all clubs or a selected club
        # Allow club members to only view projects of their clubs
        if not request.user.is_secretary:
            # Filter projects of all clubs for which the user is a member
            queryset = queryset.filter(
                clubs__roles__members__id__contains=request.user.id)

        if club_id != -1:
            queryset = queryset.filter(clubs__id__contains=club_id)

        if only_my_projects:
            queryset = queryset.filter(members__id__contains=request.user.id)

        return queryset


class ProjectMembershipFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
        1. Users to see members of only their clubs' projects by default
        2. Users to see members of a specific clubs' projects based on request
        2. Users to see members of a specific project based on request
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return project memberships for'
                                      + ' this Club',
                          type='integer'),
            coreapi.Field(name='project_id', location='query', required=False,
                          description='Only return project memberships for'
                                      + ' this Project',
                          type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            project_id = int(request.query_params.get('project_id', -1))
        except:
            raise ParseError

        # Filter memberships of projects of all clubs for which the user
        # is a member
        queryset = queryset.filter(
            project__clubs__roles__members__id__contains=request.user.id)

        if club_id != -1:
            queryset = queryset.filter(project__clubs__id__contains=club_id)

        if project_id != -1:
            queryset = queryset.filter(project=project_id)

        return queryset


class PostFilter(rest_framework_filters.BaseFilterBackend):
    """
    Filter that allows:
    1. Users to see posts by channels that they have subscribed
    or of a selected channel
    2. Impose an ascending or descending order on the posts
    as per their `created` attribute
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='channel_id', location='query', required=False,
                          description='Only return Posts for this Channel',
                          type='integer'),
            coreapi.Field(name='order', location='query', required=False,
                          description='Order most recent post first if set to'
                                      + ' -1 or unset, otherwise reverse the order',
                          type='integer'),
        ]

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

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='parent_id', location='query', required=False,
                          description='Only return Conversations that are'
                                      + ' children of this Conversation.',
                          type='integer'),
            coreapi.Field(name='channel_id', location='query', required=False,
                          description='Only return Conversations for this'
                                      + ' Channel', type='integer'),
            coreapi.Field(name='order', location='query', required=False,
                          description='Order most recent Conversation first if'
                                      + ' set to -1 or unset, otherwise reverse the order',
                          type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only Conversations authored by'
                                      + ' the current user, if set to a non-zero value.',
                          type='integer'),
        ]

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

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return Channels for this'
                                      + ' Club', type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only Channels subscribed by'
                                      + ' the current user, if set to a non-zero value.',
                          type='integer'),
        ]

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
    Filter that only allows:
    1. Users to see feedback replies for clubs that they are representative of
    2. Secretaries to see all the feedback replies
    3. Users to see the replies to feedbacks posted by them
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(name='club_id', location='query', required=False,
                          description='Only return FeedbackReplies for this'
                                      + ' Club', type='integer'),
            coreapi.Field(name='only_my', location='query', required=False,
                          description='Return only replies to the Feedbacks '
                                      + 'posted by current user if set to a non-zero value.',
                          type='integer'),
            coreapi.Field(name='order', location='query', required=False,
                          description='Order most recently posted reply'
                                      + ' first if set to -1 or unset, otherwise reverse the'
                                      + ' order', type='integer'),
        ]

    def filter_queryset(self, request, queryset, view):
        try:
            club_id = int(request.query_params.get('club_id', -1))
            order = int(request.query_params.get('order', -1))
            only_my_feedbacks = bool(int(
                request.query_params.get('only_my', 0)))
        except:
            raise ParseError

        # Allow secretary to view feedback replies for all or selected clubs
        if not request.user.is_secretary:
            # Filter feedback replies of all clubs for which the user
            # is representative or the replies to feedbacks which have
            # been posted by the user
            club_list = models.Club.objects.filter(
                roles__privilege=constants.PRIVILEGE_REP,
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
