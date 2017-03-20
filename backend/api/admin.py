from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from . import models


# Register your models here.
class UserAdmin(AbstractUserAdmin):
    model = models.User

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Club)
admin.site.register(models.Project)
admin.site.register(models.Feedback)
admin.site.register(models.FeedbackReply)
admin.site.register(models.Channel)
admin.site.register(models.Post)
admin.site.register(models.Conversation)
admin.site.register(models.ClubRole)
