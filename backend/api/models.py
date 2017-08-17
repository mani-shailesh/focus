"""
Defines the models used in the app.
"""

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

from . import constants


class User(AbstractUser):
    """
    Wrapper for the AbstractUser to make it easy to modify User later.
    """

    def is_secretary(self):
        """
        Returns true if this User is `secretary`, false otherwise
        """
        # TODO
        return self.is_superuser


class Club(models.Model):
    """
    Model to represent a Club.
    """
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    requests = models.ManyToManyField('User', through='ClubMembershipRequest')

    def __unicode__(self):
        return self.name

    def has_member(self, user):
        """
        Returns true if `user` is a member of this Club, false otherwise
        """
        return ClubMembership.objects.filter(
            user__id=user.id, club_role__club=self
        ).exists()

    def has_rep(self, user):
        """
        Returns true if `user` is a representative of this Club, false
        otherwise
        """
        return ClubMembership.objects.filter(
            user__id=user.id,
            club_role__club=self,
            club_role__privilege=constants.PRIVILEGE_REP
        ).exists()


class ClubMembershipRequest(models.Model):
    """
    Model to represent a request made by a User for membership in a Club
    """
    STATUS_CHOICES = (
        ('PD', 'Pending'),
        ('AC', 'Accepted'),
        ('RE', 'Rejected'),
        ('CN', 'Cancelled'),
    )
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    initiated = models.DateTimeField(auto_now_add=True, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                              blank=False, default='PD')
    closed = models.DateTimeField(default=None, blank=True, null=True)

    def __unicode__(self):
        return '{} requested membership in {} on {} : {}'.format(
            self.user, self.club, self.initiated, self.status)


class ClubRole(models.Model):
    """
    Model to represent a specific role for members in a given Club
    """
    PRIVILEGE_CHOICES = (
        (constants.PRIVILEGE_REP, 'Representative'),
        (constants.PRIVILEGE_MEM, 'Member')
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False,
                             related_name='roles')
    members = models.ManyToManyField('User', through='ClubMembership')
    privilege = models.CharField(max_length=3, choices=PRIVILEGE_CHOICES,
                                 blank=False, default='MEM')

    def __unicode__(self):
        return '{} in {}'.format(self.name, self.club)


class ClubMembership(models.Model):
    """
    Model to represent membership of a User in a Club through a ClubRole
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    club_role = models.ForeignKey('ClubRole', on_delete=models.CASCADE,
                                  blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return '{} is {} since {}'.format(self.user, self.club_role,
                                          self.joined)


class Project(models.Model):
    """
    Model to represent a Project underataken by Club(s)
    """
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    started = models.DateTimeField(auto_now_add=True, blank=False)
    closed = models.DateTimeField(default=None, blank=True, null=True)
    leader = models.ForeignKey('User', on_delete=models.PROTECT, blank=False,
                               related_name='lead_projects')
    members = models.ManyToManyField('User', through='ProjectMembership')
    clubs = models.ManyToManyField('Club', through='ClubProject')

    def __unicode__(self):
        return str(self.name)


class ClubProject(models.Model):
    """
    Model to represent relationship between Club and Project.
    """
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                blank=False)

    def __unicode__(self):
        return '{} has undertaken {}'.format(self.club, self.project)


class ProjectMembership(models.Model):
    """
    Model to represent membership of User in a Project
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return '{} is working on {}'.format(self.user, self.project)


class Channel(models.Model):
    """
    Model to represent a communication channel of a Club
    """
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.OneToOneField('Club', on_delete=models.CASCADE, blank=False)
    subscribers = models.ManyToManyField('User', through='ChannelSubscription')

    def __unicode__(self):
        return '{} : {}'.format(self.name, self.club)


class ChannelSubscription(models.Model):
    """
    Model to represent a User's subscription to a Channel
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE,
                                blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)

    def __unicode__(self):
        return '{} subscribes to {}'.format(self.user, self.channel)


class Post(models.Model):
    """
    Model to represent a public post in a Channel
    """
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE,
                                blank=False)

    def __unicode__(self):
        return 'Post in {} at {}'.format(self.channel, self.created)


class Conversation(models.Model):
    """
    Model to represent private conversations in a Channel
    """
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE,
                                blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    parent = models.ForeignKey('Conversation', on_delete=models.CASCADE,
                               default=None, blank=True, null=True)

    def __unicode__(self):
        return 'Conversation in {} by {} at {}'.format(
            self.channel, self.author, self.created)


class Feedback(models.Model):
    """
    Model to represent a Feedback for a Club
    """
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)

    def __unicode__(self):
        return 'Feedback for {} by {}'.format(self.club, self.author)


class FeedbackReply(models.Model):
    """
    Model to represent reply to a Feedback by the Club
    """
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    parent = models.OneToOneField('Feedback', on_delete=models.CASCADE,
                                  blank=False)

    def __unicode__(self):
        return 'Reply to {}'.format(self.parent)
