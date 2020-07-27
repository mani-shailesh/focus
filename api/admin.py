"""
This module declares Admin class and registers Models to it.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin

from . import models


class UserAdmin(AbstractUserAdmin):
    """
    Wrapper class for AbstractUserAdmin.
    """
    model = models.User

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets += (('Administration', {'fields': ('is_secretary',)}),)
        return fieldsets


# Register the models.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Club)
admin.site.register(models.Project)
admin.site.register(models.ProjectMembership)
admin.site.register(models.ClubProject)
admin.site.register(models.Feedback)
admin.site.register(models.FeedbackReply)
admin.site.register(models.Channel)
admin.site.register(models.Post)
admin.site.register(models.Conversation)
admin.site.register(models.ClubRole)
admin.site.register(models.ClubMembershipRequest)
admin.site.register(models.ClubMembership)
