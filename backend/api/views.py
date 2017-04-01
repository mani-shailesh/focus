from . import models, serializers, permissions, filters
from rest_framework import generics
from rest_framework import permissions as rest_permissions
from rest_framework import filters as rest_filters


class UserList(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = models.User.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSelfOrReadOnlyUser)
    serializer_class = serializers.UserSerializer


class ClubList(generics.ListCreateAPIView):
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          rest_permissions.DjangoModelPermissions)
    filter_backends = (rest_filters.SearchFilter,
                       filters.MyClubsFilterBackend)
    search_fields = ('name',)


class ClubDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Club.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrRepOrReadOnlyClub)
    serializer_class = serializers.ClubDetailSerializer


class ClubRoleList(generics.ListCreateAPIView):
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer
    filter_backends = (filters.MyClubRolesFilterBackend,)


class ClubRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ClubRole.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepClubRole)
    serializer_class = serializers.ClubRoleSerializer


class ClubMembershipList(generics.ListAPIView):
    queryset = models.ClubMembership.objects.all()
    serializer_class = serializers.ClubMembershipSerializer
    filter_backends = (filters.MyClubMembershipsFilterBackend,)


class ClubMembershipDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ClubMembership.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsRepClubMembership)
    serializer_class = serializers.ClubMembershipSerializer


class ChannelList(generics.ListAPIView):
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer


class ChannelDetail(generics.RetrieveUpdateAPIView):
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer


class PostList(generics.ListCreateAPIView):
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        """
        This view should return a list of all the posts for channels subscribed by the user.
        """
        return models.Post.objects.filter(channel__subscribers__id__contains=self.request.user.id)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer


class ConversationList(generics.ListCreateAPIView):
    serializer_class = serializers.ConversationSerializer

    def get_queryset(self):
        """
        This view should return a list of all the conversations for channels subscribed by the user.
        """
        return models.Conversation.objects.filter(channel__club__roles__members__id__contains=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ConversationDetail(generics.RetrieveAPIView):
    queryset = models.Conversation.objects.all()
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsClubMemberReadOnlyPost)
    serializer_class = serializers.ConversationSerializer


class ProjectList(generics.ListCreateAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.MyProjectsFilterBackend,)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectDetailSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrClubMemberProject)


class FeedbackList(generics.ListCreateAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    filter_backends = (filters.MyClubFeedbacksFilterBackend,)


class FeedbackDetail(generics.RetrieveAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackDetailSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrRepOrAuthorFeedback)


class FeedbackReplyCreate(generics.CreateAPIView):
    serializer_class = serializers.FeedbackReplySerializer


class FeedbackReplyDetail(generics.RetrieveAPIView):
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplyDetailSerializer
    permission_classes = (rest_permissions.IsAuthenticated,
                          permissions.IsSecyOrRepOrAuthorFeedbackReply)
