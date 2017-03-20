from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    requests = models.ManyToManyField('User', through='ClubMembershipRequest')

    def __str__(self):
        return self.name


class ClubMembershipRequest(models.Model):
    STATUS_CHOICES = (
        ('PD', 'Pending'),
        ('AC', 'Accepted'),
        ('RE', 'Rejected'),
        ('CN', 'Cancelled'),
    )
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    initiated = models.DateTimeField(auto_now_add=True, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=False, default='PD')
    closed = models.DateTimeField(default=None, blank=True, null=True)


class ClubRole(models.Model):
    PRIVILEGE_CHOICES = (
        ('REP', 'Representative'),
        ('MEM', 'Member')
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False, related_name='roles')
    members = models.ManyToManyField('User', through='ClubMembership')
    privilege = models.CharField(max_length=3, choices=PRIVILEGE_CHOICES, blank=False, default='MEM')

    def __str__(self):
        return str(self.club) + " " + str(self.name)


class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    club_role = models.ForeignKey('ClubRole', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Project(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    started = models.DateTimeField(auto_now_add=True, blank=False)
    closed = models.DateTimeField(default=None, blank=True, null=True)
    leader = models.ForeignKey('User', on_delete=models.PROTECT, blank=False, related_name='lead_projects')
    members = models.ManyToManyField('User', through='ProjectMembership')
    clubs = models.ManyToManyField('Club', through='ClubProject')

    def __str__(self):
        return str(self.name)


class ClubProject(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False)


class ProjectMembership(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Channel(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.OneToOneField('Club', on_delete=models.CASCADE, blank=False)
    subscribers = models.ManyToManyField('User', through='ChannelSubscription')

    def __str__(self):
        return str(self.club) + " " + str(self.name)


class ChannelSubscription(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Post(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.channel) + " " + str(self.created)


class Conversation(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    parent = models.ForeignKey('Conversation', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.channel) + " " + str(self.created)


class Feedback(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.club) + " " + str(self.created)


class FeedbackReply(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    parent = models.OneToOneField('Feedback', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.parent) + " " + str(self.created)
