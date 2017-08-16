"""
This module contains the controllers attached to the API endpoints.
"""

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions as rest_permissions
from rest_framework import filters as rest_filters
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
                          permissions.IsSelfOrReadOnlyUser)


class ClubViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a Club
    """
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          rest_permissions.DjangoModelPermissions,
                          permissions.IsSecyOrRepOrReadOnlyClub)
    filter_backends = (rest_filters.SearchFilter,
                       filters.MyClubsFilterBackend)
    search_fields = ('name',)

    @detail_route(methods=['get'])
    def members(self, request, pk=None):
        """
        Return a list of the Users who are members of this club as response.
        """
        club = self.get_object()
        queryset = models.User.objects.filter(clubrole__club=club).distinct()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.UserSerializer(queryset, many=True)
        return Response(serializer.data)


class ClubRoleViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a ClubRole
    """
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepOrMemReadOnlyClubRole)
    filter_backends = (filters.MyClubRolesFilterBackend,)


class ClubMembershipViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for ClubMembership
    """
    queryset = models.ClubMembership.objects.all()
    serializer_class = serializers.ClubMembershipSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepOrMemReadOnlyClubMembership)
    filter_backends = (filters.MyClubMembershipsFilterBackend,)


class ChannelViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Channels
    """
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)
    filter_backends = (rest_filters.SearchFilter,
                       filters.MyChannelsFilterBackend)
    search_fields = ('name',)
    
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


class PostViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Posts.
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.MyPostsFilterBackend)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepOrReadOnlyPost)
    search_fields = ('content',)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for Conversations.
    """
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.MyConversationsFilterBackend)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsClubMemberReadOnlyConversation)
    search_fields = ('content',)

    def perform_create(self, serializer):
        """
        Override create to make sure that current user
        is automatically registered as the author
        """
        serializer.save(author=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Viewset to provide actions for a Project 
    """
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepOrSecyAndClubMemberReadOnlyProject)
    filter_backends = (filters.MyProjectsFilterBackend,)


class FeedbackList(generics.ListCreateAPIView):
    """
    View to return the list of feedbacks as specified by query
    parameters and to create feedbacks
    """
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    filter_backends = (filters.MyClubFeedbacksFilterBackend,)


class FeedbackDetail(generics.RetrieveAPIView):
    """
    View to allow retrieval of a feedback details based on
    appropriate permissions
    """
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackDetailSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrRepOrAuthorFeedback)


class FeedbackReplyCreate(generics.CreateAPIView):
    """
    View to create feedback replies
    """
    serializer_class = serializers.FeedbackReplySerializer


class FeedbackReplyDetail(generics.RetrieveAPIView):
    """
    View to allow retrieval of a feedback reply details based on
    appropriate permissions
    """
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplyDetailSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrRepOrAuthorFeedbackReply)
