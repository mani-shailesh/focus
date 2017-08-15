"""
This modules contains classes to define serialization of Models.
"""

from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User.
    """
    date_joined = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.User
        fields = ('id', 'username', 'date_joined', 'first_name',
                  'last_name', 'email')


class ClubSerializer(serializers.ModelSerializer):
    """
    Compact serializer for Club.
    """
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.Club
        fields = ('id', 'name', 'description')


class ClubRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for a ClubRole.
    """
    class Meta:
        model = models.ClubRole
        fields = ('id', 'name', 'description', 'club', 'privilege')


class ClubMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer to represent membership of a User in a Club through a ClubRole.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all())
    club_role = serializers.PrimaryKeyRelatedField(
        queryset=models.ClubRole.objects.all())

    class Meta:
        model = models.ClubMembership
        fields = ('id', 'user', 'club_role', 'joined')


class ProjectSerializer(serializers.ModelSerializer):
    """
    Compact serializer for a Project.
    """
    class Meta:
        model = models.Project
        fields = ('id', 'name', 'description')


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a Project.
    """
    started = serializers.ReadOnlyField()

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'description', 'started',
                  'closed', 'leader', 'members', 'clubs')


class ChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for a Channel.
    """
    club = ClubSerializer(read_only=True)

    class Meta:
        model = models.Channel
        fields = ('id', 'name', 'description', 'club')


class PostSerializer(serializers.ModelSerializer):
    """
    Compact serializer for a Post.
    """
    created = serializers.ReadOnlyField()

    class Meta:
        model = models.Post
        fields = ('id', 'content', 'created', 'channel')


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for a Conversation.
    """
    author = serializers.ReadOnlyField(source='author.username')
    created = serializers.ReadOnlyField()

    class Meta:
        model = models.Conversation
        fields = ('id', 'content', 'created', 'channel', 'author', 'parent')


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a Conversation.
    """
    author = serializers.ReadOnlyField(source='author.username')
    created = serializers.ReadOnlyField()
    parent = ConversationSerializer(read_only=True)

    class Meta:
        model = models.Conversation
        fields = ('id', 'content', 'created', 'channel', 'author', 'parent')


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for a Feedback.
    """
    created = serializers.ReadOnlyField()
    feedbackreply = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Feedback
        fields = ('id', 'content', 'created', 'club',
                  'author', 'feedbackreply')


class FeedbackReplySerializer(serializers.ModelSerializer):
    """
    Serializer for a FeedbackReply.
    """
    created = serializers.ReadOnlyField()

    class Meta:
        model = models.FeedbackReply
        fields = ('id', 'content', 'created')


class FeedbackDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a Feedback.
    """
    created = serializers.ReadOnlyField()
    feedbackreply = FeedbackReplySerializer(read_only=True)

    class Meta:
        model = models.Feedback
        fields = ('id', 'content', 'created', 'club',
                  'author', 'feedbackreply')


class FeedbackReplyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a FeedbackReply.
    """
    created = serializers.ReadOnlyField()
    parent = FeedbackSerializer(read_only=True)

    class Meta:
        model = models.FeedbackReply
        fields = ('id', 'content', 'created', 'parent')
