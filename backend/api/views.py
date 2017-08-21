"""
This module contains the controllers attached to the API endpoints.
"""

from rest_framework import viewsets
from rest_framework import permissions as rest_permissions
from rest_framework import filters as rest_filters
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models, serializers, permissions, filters


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions related to Users.
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.UserPermission)


class ClubViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a Club
    """
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          rest_permissions.DjangoModelPermissions,
                          permissions.ClubPermission)
    filter_backends = (rest_filters.SearchFilter,
                       filters.ClubFilter)
    search_fields = ('name',)


class ClubMembershipRequestViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a ClubMembershipRequest
    """
    queryset = models.ClubMembershipRequest.objects.all()
    serializer_class = serializers.ClubMembershipRequestSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubMembershipRequestPermission,)
    filter_backends = (filters.ClubMembershipRequestFilter,)

    def perform_create(self, serializer):
        """
        Override create to make sure that the current user
        is only able to make requests for herself.
        """
        serializer.save(user=self.request.user)

    @detail_route(methods=['get'])
    def accept(self, request, pk=None):
        """
        Accept the request if the current user is representative of the club
        for which request is made and if the request is still pending.
        """
        membership_request = self.get_object()
        if not membership_request.club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        membership_request.accept()
        serializer = self.serializer_class(membership_request)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def reject(self, request, pk=None):
        """
        Reject the request if the current user is representative of the club
        for which request is made and if the request is still pending.
        """
        membership_request = self.get_object()
        if not membership_request.club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        membership_request.reject()
        serializer = self.serializer_class(membership_request)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def cancel(self, request, pk=None):
        """
        Accept the request if the current user has initiated this request and
        the request is still pending.
        """
        membership_request = self.get_object()
        if not membership_request.user == request.user:
            raise rest_exceptions.PermissionDenied()
        membership_request.cancel()
        serializer = self.serializer_class(membership_request)
        return Response(serializer.data)

class ClubRoleViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a ClubRole
    """
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubRolePermission)
    filter_backends = (filters.ClubRoleFilter,)


class ClubMembershipViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for ClubMembership
    """
    queryset = models.ClubMembership.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubMembershipPermission)
    filter_backends = (filters.ClubMembershipFilter,)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update':
            return serializers.ClubMembershipEditSerializer
        return serializers.ClubMembershipSerializer

    def update(self, request, *args, **kwargs):
        """
        Override update to make sure that only valid clubRole is assigned after
        updation.
        """
        club_membership = self.get_object()
        serializer = self.get_serializer(club_membership,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        if not club_membership.club_role.club \
           .has_role(serializer.validated_data['club_role']):
            raise rest_exceptions.ValidationError(
                'Invalid Club Role ID for this Club!')
        return super(ClubMembershipViewSet, self).update(request, args, kwargs)


class ChannelViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Channels
    """
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)
    filter_backends = (rest_filters.SearchFilter,
                       filters.ChannelFilter)
    search_fields = ('name',)

    @detail_route(methods=['get'])
    def subscribe(self, request, pk=None):
        """
        Subscribe the logged in user to this Channel.
        """
        channel = self.get_object()
        channel.subscribe(request.user)
        serializer = serializers.ChannelSerializer(
            channel,
            context={'request': request}
        )
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def subscribers(self, request, pk=None):
        """
        Return a list of the Users who are subscribers of this Channel
        as response.
        """
        channel = self.get_object()
        queryset = models.User.objects.filter(channel=channel)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def unsubscribe(self, request, pk=None):
        """
        Unsubscribe the logged in user from this Channel.
        Safe to use even if the user is not subscribed.
        """
        channel = self.get_object()
        channel.unsubscribe(request.user)
        serializer = serializers.ChannelSerializer(
            channel,
            context={'request': request}
        )
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Posts.
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.PostFilter)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.PostPermission)
    search_fields = ('content',)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Conversations.
    """
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.ConversationFilter)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ConversationPermission)
    search_fields = ('content',)

    def perform_create(self, serializer):
        """
        Override create to make sure that current user
        is automatically registered as the author
        """
        serializer.save(author=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Project
    """
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ProjectPermission)
    filter_backends = (filters.ProjectFilter,)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Feedback
    """
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.FeedbackPermission)
    filter_backends = (filters.FeedbackFilter,)


class FeedbackReplyViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for FeedbackReply
    """
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplySerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.FeedbackReplyPermission)
    filter_backends = (filters.FeedbackReplyFilter,)

    def create(self, request, *args, **kwargs):
        serializer = serializers.FeedbackReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.validated_data['parent']
        if not feedback.club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(FeedbackReplyViewSet, self).create(request, args, kwargs)
