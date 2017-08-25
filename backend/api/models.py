"""
Defines the models used in the app.
"""

from __future__ import unicode_literals
from datetime import datetime

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from . import constants, exceptions


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

    def save(self, *args, **kwargs):
        """
        Override save() to make sure that whenever a new Club is created, an
        associated Channel is also created.
        """
        if not self.pk:
            with transaction.atomic():
                super(Club, self).save(*args, **kwargs)
                Channel.objects.create(
                    name='{} Channel'.format(self.name),
                    description='Default channel for {}'.format(self.name),
                    club=self,
                )
        else:
            super(Club, self).save(*args, **kwargs)

    def add_member(self, user, privilege=constants.PRIVILEGE_MEM):
        """
        Adds `user` as a member of this Club.
        """
        club_role, created = ClubRole.objects.get_or_create(
            name=constants.DISPLAY_NAME[privilege],
            description='{} of {}'.format(constants.DISPLAY_NAME[privilege],
                                          self.name),
            club=self,
            privilege=privilege,
        )
        ClubMembership.objects.get_or_create(
            club_role=club_role,
            user=user,
        )

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

    def has_role(self, club_role):
        """
        Returns true if `club_role` is id of a valid ClubRole for this Club.
        """
        return club_role.club == self

    def has_pending_request(self, user):
        """
        Returns True if there is a pending ClubMembershipRequest from `user`,
        False otherwise.
        """
        return ClubMembershipRequest.objects.filter(
            user=user,
            club=self,
            status=constants.REQUEST_STATUS_PENDING
        ).exists()


class ClubMembershipRequest(models.Model):
    """
    Model to represent a request made by a User for membership in a Club
    """
    STATUS_CHOICES = (
        (constants.REQUEST_STATUS_PENDING,
         constants.DISPLAY_NAME[constants.REQUEST_STATUS_PENDING]),
        (constants.REQUEST_STATUS_ACCEPTED,
         constants.DISPLAY_NAME[constants.REQUEST_STATUS_ACCEPTED]),
        (constants.REQUEST_STATUS_REJECTED,
         constants.DISPLAY_NAME[constants.REQUEST_STATUS_REJECTED]),
        (constants.REQUEST_STATUS_CANCELLED,
         constants.DISPLAY_NAME[constants.REQUEST_STATUS_CANCELLED]),
    )
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    initiated = models.DateTimeField(auto_now_add=True, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                              blank=False,
                              default=constants.REQUEST_STATUS_PENDING)
    closed = models.DateTimeField(default=None, blank=True, null=True)

    def __unicode__(self):
        return '{} requested membership in {} on {} : {}'.format(
            self.user, self.club, self.initiated, self.get_status_display())

    def is_pending(self):
        """
        Returns `True` if this request is still pending, `False` otherwise.
        """
        return self.status == constants.REQUEST_STATUS_PENDING

    def accept(self):
        """
        Marks the status of this request as 'Accepted' if it is pending, throws
        ActionNotAllowed Exception otherwise.
        """
        if not self.is_pending():
            raise exceptions.ActionNotAvailable(
                action='accept',
                detail='The request is already marked as ' +
                self.get_status_display() + '. Can not be accepted!'
            )

        with transaction.atomic():
            """
            Make sure that the user becomes a member if the request is Accepted
            otherwise accepting request fails as well.
            """
            self.status = constants.REQUEST_STATUS_ACCEPTED
            self.closed = datetime.now()
            self.club.add_member(self.user)
            self.save()

    def reject(self):
        """
        Marks the status of this request as 'Rejected' if it is pending, throws
        ActionNotAllowed Exception otherwise.
        """
        if not self.is_pending():
            raise exceptions.ActionNotAvailable(
                action='reject',
                detail='The request is already marked as ' +
                self.get_status_display() + '. Can not be rejected!'
            )
        self.status = constants.REQUEST_STATUS_REJECTED
        self.closed = datetime.now()
        self.save()

    def cancel(self):
        """
        Marks the status of this request as 'Cancelled' if it is pending,
        throws ActionNotAllowed Exception otherwise.
        """
        if not self.is_pending():
            raise exceptions.ActionNotAvailable(
                action='cancel',
                detail='The request is already marked as ' +
                self.get_status_display() + '. Can not be cancelled!'
            )
        self.status = constants.REQUEST_STATUS_CANCELLED
        self.closed = datetime.now()
        self.save()


class ClubRole(models.Model):
    """
    Model to represent a specific role for members in a given Club
    """
    PRIVILEGE_CHOICES = (
        (constants.PRIVILEGE_REP,
         constants.DISPLAY_NAME[constants.PRIVILEGE_REP]),
        (constants.PRIVILEGE_MEM,
         constants.DISPLAY_NAME[constants.PRIVILEGE_MEM]),
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False,
                             related_name='roles')
    members = models.ManyToManyField('User', through='ClubMembership')
    privilege = models.CharField(max_length=3, choices=PRIVILEGE_CHOICES,
                                 blank=False, default=constants.PRIVILEGE_MEM)

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

    def has_member(self, user):
        """
        Returns True if `user` is a member of this Project, False otherwise.
        """
        return self.has_leader(user) or ProjectMembership.objects.filter(
            user=user,
            project=self,
        ).exists()

    def has_leader(self, user):
        """
        Returns True if `user` is a leader of this Project, False otherwise.
        """
        return self.leader == user

    def has_club_rep(self, user):
        """
        Returns True if `user` is a representative of one of the parent Clubs
        of this Project, False otherwise.
        """
        return ClubMembership.objects.filter(
            user=user,
            club_role__club__in=self.clubs.all(),
            club_role__privilege=constants.PRIVILEGE_REP,
        ).exists()

    def has_club_member(self, user):
        """
        Returns True if `user` is a member of one of the parent Clubs
        of this Project, False otherwise.
        """
        return ClubMembership.objects.filter(
            user=user,
            club_role__club__in=self.clubs.all(),
        ).exists()


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

    def has_subscriber(self, user):
        """
        Returns true if `user` is a subscriber of this Channel, false
        otherwise.
        """
        return ChannelSubscription.objects.filter(
            user=user,
            channel=self,
        ).exists()

    def subscribe(self, user):
        """
        Subscribe `user` to this Channel.
        Safe to use even if the `user` has already subscribed.
        """
        ChannelSubscription.objects.get_or_create(
            user=user,
            channel=self,
        )

    def unsubscribe(self, user):
        """
        Unsubscribe `user` from this Channel.
        Safe to use even if the `user` has not subscribed.
        """
        ChannelSubscription.objects.filter(
            user=user,
            channel=self,
        ).delete()


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

    def is_replied(self):
        """
        Returns `True` if this Feedback has been replied, `False` otherwise
        """
        return FeedbackReply.objects.filter(
            parent=self,
        ).exists()

    def get_reply(self):
        """
        Returns the FeedbackReply object for this Feedback if it has been
        replied to, raises FeedbackReply.DoesNotExist otherwise.
        """
        return FeedbackReply.objects.get(parent=self)


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
