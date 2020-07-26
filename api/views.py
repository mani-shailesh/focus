"""
This module contains the controllers attached to the API endpoints.
"""

from rest_framework import exceptions as rest_exceptions
from rest_framework import filters as rest_filters
from rest_framework import permissions as rest_permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers, permissions, filters, exceptions
from . import viewsets as custom_viewsets


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
        Return the details of given User.
    list:
        Return a list of all the existing Users.
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)


class ClubViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return the details of given Club.
    list:
        Return a list of all the existing Clubs.
    create:
        Create a new Club. Only a secretary is allowed to create a new Club.
    update:
        Update the Club details. Only representative of the Club or a secretary
        can update the Club details.
    delete:
        Delete the given Club. Only a secretary is allowed to delete the Club.
    """
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubPermission)
    filter_backends = (rest_filters.SearchFilter,
                       filters.ClubFilter)
    search_fields = ('name',)

    def create(self, request, *args, **kwargs):
        """
        Create a new Club. Only a secretary is allowed to create a new Club.
        """
        if not request.user.is_secretary():
            raise rest_exceptions.PermissionDenied()
        return super(ClubViewSet, self).create(request, *args, **kwargs)


class ClubMembershipRequestViewSet(custom_viewsets.CreateListRetrieveViewSet):
    """
    retrieve:
        Return the details of given ClubMembershipRequest.
    list:
        Return a list of all the ClubMembershipRequests posted by the current
        user and the ClubMembershipRequests made for a Club that the current
        user is a representative of.
    create:
        Create a new ClubMembershipRequest. Only non-members of a Club can
        request for it's membership if they do not have a pending request
        already.

    """
    queryset = models.ClubMembershipRequest.objects.all()
    serializer_class = serializers.ClubMembershipRequestSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubMembershipRequestPermission,)
    filter_backends = (filters.ClubMembershipRequestFilter,)

    def create(self, request, *args, **kwargs):
        """
        Create a new ClubMembershipRequest. Only non-members of a Club can
        request for it's membership if they do not have a pending request
        already.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = serializer.validated_data['club']
        if club.has_member(request.user):
            raise exceptions.ActionNotAvailable(
                action='create',
                detail='You are already a member!'
            )
        if club.has_pending_request(request.user):
            raise exceptions.ActionNotAvailable(
                action='create',
                detail='You already have a pending request for this club!'
            )
        return super(ClubMembershipRequestViewSet, self).create(
            request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Override create to make sure that the current user
        is only able to make requests for herself.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'])
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

    @action(detail=True, methods=['put'])
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

    @action(detail=True, methods=['put'])
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
    retrieve:
        Return the details of given ClubRole if current user is a member of the
        correspoinding Club.
    list:
        Return a list of all the existing ClubRoles in the Clubs that the
        current User is a member of.
    create:
        Create a new ClubRole. Only representative of the Club is
        authorized for this.
    update:
        Update the ClubRole details. Only representative of the Club is
        authorized for this.
    delete:
        Delete the given ClubRole. Only representative of the Club is
        authorized for this.
    """
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubRolePermission)
    filter_backends = (filters.ClubRoleFilter,)


class ClubMembershipViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return the details of given ClubMembership if current user is a member
        of the correspoinding Club.
    list:
        Return a list of ClubMembership for all Clubs or of a specific Club.
    create:
        Create a new ClubMembership directly(without going through the
        ClubMembershipRequest). Only a secretary is authorized for this.
    update:
        Update the ClubMembership details. Only representative of the Club or a
        secretary is authorized for this.
    delete:
        Delete the ClubMembership details. Only representative of the Club or a
        secretary is authorized for this.
    """
    queryset = models.ClubMembership.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ClubMembershipPermission)
    filter_backends = (filters.ClubMembershipFilter,)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update' or \
                self.action == 'create':
            return serializers.ClubMembershipEditSerializer
        return serializers.ClubMembershipSerializer

    def update(self, request, *args, **kwargs):
        """
        Update the ClubMembership details. Only representative of the Club or a
        secretary is authorized for this.
        """
        club_membership = self.get_object()
        serializer = self.get_serializer(club_membership,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        if club_membership.user != serializer.validated_data['user']:
            raise rest_exceptions.ValidationError(
                'You can not update the User!'
            )
        if not club_membership.club_role.club \
                .has_role(serializer.validated_data['club_role']):
            raise rest_exceptions.ValidationError(
                'Invalid Club Role ID for this Club!')
        return super(ClubMembershipViewSet, self).update(
            request, *args, **kwargs)


class ChannelViewSet(custom_viewsets.UpdateListRetrieveViewSet):
    """
    retrieve:
        Return the details of the given Channel.
    list:
        Return a list of all Channels filtered by the given query params.
    update:
        Update the Channel details. Only representative of the corresponding
        Club is authorized for this.
    """
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ChannelPermission)
    filter_backends = (rest_filters.SearchFilter,
                       filters.ChannelFilter)
    search_fields = ('name',)

    @action(detail=True, methods=['put'])
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

    @action(detail=True, methods=['get'])
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

    @action(detail=True, methods=['put'])
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
    retrieve:
        Return the details of given Post.
    list:
        Return a list of all the Posts from Channels subscribed by the current
        User, if no other option is provided. Otherwise, return the results
        based on the provided options.
    create:
        Create a new Post. Only representative of the Club is
        authorized for this.
    update:
        Update the Post details. Only representative of the Club is
        authorized for this.
    delete:
        Delete the given Post. Only representative of the Club is
        authorized for this.
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.PostFilter)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.PostPermission)
    search_fields = ('content',)

    def create(self, request, *args, **kwargs):
        """
        Create a new Post. Only representative of the Club is
        authorized for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = serializer.validated_data['channel'].club
        if not club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(PostViewSet, self).create(request, *args, **kwargs)


class ConversationViewSet(custom_viewsets.CreateListRetrieveViewSet):
    """
    retrieve:
        Return the details of the given Conversation. Only members of the
        correspoinding Club are authorized for this.
    list:
        Return a list of all the Conversations on Channels of the Clubs that
        the current User is a member of. Also, filter and order the results
        based on the provided query parameters.
    create:
        Create a new Conversation. Only members of the Club are authorized
        for this.
    """
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    filter_backends = (rest_filters.SearchFilter,
                       filters.ConversationFilter)
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ConversationPermission)
    search_fields = ('content',)

    def create(self, request, *args, **kwargs):
        """
        Create a new Conversation. Only members of the Club are authorized
        for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = serializer.validated_data['channel'].club
        if not club.has_member(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(ConversationViewSet, self).create(
            request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Make sure that the current user is automatically registered as the
        author
        """
        serializer.save(author=self.request.user)


class ProjectViewSet(custom_viewsets.ReadWriteOnlyViewSet):
    """
    retrieve:
        Return the details of given Project. Only the members of the Club or a
        secretary is authorized for this.
    list:
        Return a list of all the Projects of the Clubs that the user is a
        member of. For a secretary, return the Projects of all the Clubs. Also,
        filter the results based on query parameters.
    create:
        Create a new Project. Only representative of the Club is authorized
        for this.
    update:
        Update the Project details. Only representative of the Club is
        authorized for this.
    """
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ProjectPermission)
    filter_backends = (filters.ProjectFilter,)

    def create(self, request, *args, **kwargs):
        """
        Create a new Project. Only representative of the Club is authorized
        for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        owner_club = serializer.validated_data['owner_club']
        if not owner_club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(ProjectViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=['put'])
    def reopen(self, request, pk=None):
        """
        Reopen a closed project. Safe to use even if the Project is not closed.
        Only Club rep is authorized for this.
        """
        project = self.get_object()
        if not project.owner_club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        project.reopen()
        serializer = self.serializer_class(project)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def close(self, request, pk=None):
        """
        Mark the Project as closed. Safe to use even if the Project is already
        closed. Only Club rep is authorized for this.
        """
        project = self.get_object()
        if not project.owner_club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        project.close()
        serializer = self.serializer_class(project)
        return Response(serializer.data)


class ProjectMembershipViewSet(custom_viewsets.CreateListRetrieveViewSet):
    """
    retrieve:
        Return the details of given ProjectMembership. Only the corresponding
        Club members are authorized for this.
    list:
        Return a list of all the ProjectMemberships from the Clubs that the
        current User is a member of. Also, filter the results based on the
        provided query parameters.
    create:
        Create a new ProjectMembership. Only representative of the Club or the
        Project leader is authorized for this.
    delete:
        Delete the given ProjectMembership. Only representative of the Club or
        the Project leader is authorized for this.
    """
    queryset = models.ProjectMembership.objects.all()
    serializer_class = serializers.ProjectMembershipSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.ProjectMembershipPermission)
    filter_backends = (filters.ProjectMembershipFilter,)

    def create(self, request, *args, **kwargs):
        """
        Create a new ProjectMembership. Only representative of the Club or the
        Project leader is authorized for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data['project']
        if not (project.has_leader(request.user) or
                project.has_club_rep(request.user)):
            raise rest_exceptions.PermissionDenied()
        return super(ProjectMembershipViewSet, self).create(
            request, *args, **kwargs)


class FeedbackViewSet(custom_viewsets.CreateListRetrieveViewSet):
    """
    retrieve:
        Return the details of the given Feedback. Only representative of the
        correspoinding Club or a secretary is authorized for this.
    list:
        Return a list of all the Feedbacks for Clubs that the current User is a
        representative of. Feedbacks for all Clubs are returned to the
        secretaries. Also, filter and order the results based on the provided
        query parameters.
    create:
        Create a new Feedback. Only members of the Club are authorized
        for this.
    """
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.FeedbackPermission)
    filter_backends = (filters.FeedbackFilter,)

    def create(self, request, *args, **kwargs):
        """
        Create a new Feedback. Only members of the Club are authorized
        for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = serializer.validated_data['club']
        if not club.has_member(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(FeedbackViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Make sure that current user is automatically registered as the author
        """
        serializer.save(author=self.request.user)


class FeedbackReplyViewSet(custom_viewsets.CreateListRetrieveViewSet):
    """
    retrieve:
        Return the details of the given FeedbackReply. Only the author of the
        corresponding Feedback, the representative of the Club and a secretary
        is authorized for this.
    list:
        Return a list of all the FeedbackReplies for feedbacks sent by the
        current User and FeedbackReplies for the Clubs that the current User is
        a representative of. All FeedbackReplies are returned to the
        secretaries. Also, filter and order the results based on the provided
        query parameters.
    create:
        Create a new FeedbackReply. Only representative of the Club is
        authorized for this.
    """
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplySerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.FeedbackReplyPermission)
    filter_backends = (filters.FeedbackReplyFilter,)

    def create(self, request, *args, **kwargs):
        """
        Create a new FeedbackReply. Only representative of the Club is
        authorized for this.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.validated_data['parent']
        if not feedback.club.has_rep(request.user):
            raise rest_exceptions.PermissionDenied()
        return super(FeedbackReplyViewSet, self).create(
            request, *args, **kwargs)
