from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class ClubMembershipRequest(models.Model):
    STATUS_CHOICES = (
        ('PD', 'Pending'),
        ('AC', 'Accepted'),
        ('RE', 'Rejected'),
        ('CN', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)
    initiated = models.DateTimeField(auto_now_add=True, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=False, default='PD')
    closed = models.DateTimeField(default=None)


class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    requests = models.ManyToManyField(User, through=ClubMembershipRequest)



class ClubRole(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)
    members = models.ManyToManyField(User, through=ClubMembership)


class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    club_role = models.ForeignKey(ClubRole, on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Project(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    started = models.DateTimeField(auto_now_add=True, blank=False)
    closed = models.DateTimeField(default=None)
    leader = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    members = models.ManyToManyField(User, through=ProjectMembership)


class ProjectMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Channel(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    club = models.OneToOneField(Club, on_delete=models.CASCADE, blank=False)
    subscribers = models.ManyToManyField(User, through=ChannelSubscription)


class ChannelSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Post(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=False)


class Conversation(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    parent = models.ForeignKey("Conversation", on_delete=models.CASCADE, default=None)


class Feedback(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)


class FeedbackReply(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    parent = models.OneToOneField(Feedback, on_delete=models.CASCADE, blank=False)
