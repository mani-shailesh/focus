"""
This modules contains classes to define serialization of Models.
"""

from django.conf import settings
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer
from . import models
from . import constants


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User.
    """
    date_joined = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    class Meta:
        model = models.User
        fields = ('id', 'username', 'date_joined', 'first_name',
                  'last_name', 'email')


class ClubSerializer(serializers.ModelSerializer):
    """
    Serializer for Club.
    """
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


class ClubMembershipRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for a ClubMembershipRequest.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    initiated = serializers.ReadOnlyField()
    closed = serializers.ReadOnlyField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.ClubMembershipRequest
        fields = ('id', 'user', 'club', 'initiated', 'status', 'closed')

    def get_status(self, obj):
        """
        Method to get human readable value for the status of this request.
        """
        return obj.get_status_display()


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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    privilege = serializers.SerializerMethodField()
    club = serializers.PrimaryKeyRelatedField(read_only=True,
                                              source='club_role.club')

    class Meta:
        model = models.ClubMembership
        fields = ('id', 'user', 'username', 'club', 'joined', 'privilege')

    def get_privilege(self, obj):
        """
        Method to get human readable value for the privilege of this
        membership.
        """
        return obj.club_role.get_privilege_display()


class ClubMembershipEditSerializer(serializers.ModelSerializer):
    """
    Serializer to be used for POST/PUT request to edit a ClubMembership.
    """
    joined = serializers.ReadOnlyField()

    class Meta:
        model = models.ClubMembership
        fields = ('id', 'user', 'club_role', 'joined')


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for a Project.
    """
    started = serializers.ReadOnlyField()
    closed = serializers.ReadOnlyField()

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'description', 'started', 'closed', 'leader',
                  'owner_club', 'members')

    def validate(self, data):
        """
        Check that the leader is a member of the the owner club.
        """
        club = data['owner_club']
        leader = data['leader']

        if not club.has_member(leader):
            raise serializers.ValidationError(
                'The specified leader must be a member of the owner club!'
            )
        return super(ProjectSerializer, self).validate(data)


class ProjectMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for a Project.
    """
    joined = serializers.ReadOnlyField()

    class Meta:
        model = models.ProjectMembership
        fields = ('id', 'user', 'club', 'project', 'joined')

    def validate(self, data):
        """
        Check that the user is a member of the club.
        """
        club = data['club']
        user = data['user']
        project = data['project']

        if not project.has_club_member(user):
            raise serializers.ValidationError(
                "The specified user must be a member of at least one of the "
                + "parent clubs!"
            )
        if not club.has_member(user):
            raise serializers.ValidationError(
                "The specified user must be a member of the specified club!"
            )
        return super(ProjectMembershipSerializer, self).validate(data)


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
    author = serializers.PrimaryKeyRelatedField(read_only=True)

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
        fields = ('id', 'content', 'created', 'parent')


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """
    Custom serializer to provide additional options related to the email sent
    on password rest request.
    """

    def get_email_options(self):
        """
        Override this to provide custom template and success url.
        """
        return {
            'email_template_name':
                'account/email/password_reset_key_message.txt',
            'subject_template_name':
                'account/email/password_reset_key_subject.txt',
            'extra_email_context': {
                'password_reset_url': settings.PASSWORD_RESET_URL,
            },
        }
