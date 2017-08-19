"""
This modules contains classes to define serialization of Models.
"""

from rest_framework import serializers
from . import models
from . import constants


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
    privilege = serializers.SerializerMethodField()

    class Meta:
        model = models.Club
        fields = ('id', 'name', 'description', 'privilege')

    def get_privilege(self, obj):
        """
        Method to get the privilege of current user for this Club.
        """
        user = self.context['request'].user
        if obj.has_rep(user):
            return constants.PRIVILEGE_REP 
        if obj.has_member(user):
            return constants.PRIVILEGE_MEM
        return None


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
    Serializer for a Project.
    """
    started = serializers.ReadOnlyField()

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'description', 'started', 'closed', 'leader',
                  'members', 'clubs')


class ChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for a Channel.
    """
    club = serializers.PrimaryKeyRelatedField(read_only=True) 
    subscribed = serializers.SerializerMethodField()

    class Meta:
        model = models.Channel
        fields = ('id', 'name', 'subscribed', 'description', 'club')

    def get_subscribed(self, obj):
        """
        Method to get if the current user has subscribed to this Channel.
        """
        user = self.context['request'].user
        if obj.has_subscriber(user):
            return True
        return False


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
