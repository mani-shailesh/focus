from . import models, serializers, permissions
from rest_framework import generics
from rest_framework import permissions as rest_permissions


class UserList(generics.ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class ClubList(generics.ListCreateAPIView):
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class ClubDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class ClubRoleList(generics.ListCreateAPIView):
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer


class ClubRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ClubRole.objects.all()
    serializer_class = serializers.ClubRoleSerializer


class ChannelList(generics.ListCreateAPIView):
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer


class ChannelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Channel.objects.all()
    serializer_class = serializers.ChannelSerializer


class PostList(generics.ListCreateAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer


class ConversationList(generics.ListCreateAPIView):
    queryset = models.Conversation.objects.all()
    permission_classes = (rest_permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.ConversationSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Conversation.objects.all()
    permission_classes = (rest_permissions.IsAuthenticatedOrReadOnly,
                          permissions.IsAuthorOrReadOnly)
    serializer_class = serializers.ConversationSerializer


class ProjectList(generics.ListCreateAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class FeedbackList(generics.ListCreateAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer


class FeedbackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer


class FeedbackReplyList(generics.ListCreateAPIView):
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplySerializer


class FeedbackReplyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FeedbackReply.objects.all()
    serializer_class = serializers.FeedbackReplySerializer
