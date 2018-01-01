"""
This module registers URL patterns for the 'api' app.
"""

from django.conf.urls import url, include

from . import views
from .routers import CustomDefaultRouter

# Create a router and register the Viewsets with it.
router = CustomDefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'clubs', views.ClubViewSet)
router.register(r'requests', views.ClubMembershipRequestViewSet)
router.register(r'clubRoles', views.ClubRoleViewSet)
router.register(r'clubMembers', views.ClubMembershipViewSet)
router.register(r'channels', views.ChannelViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'conversations', views.ConversationViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'projectMembers', views.ProjectMembershipViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'replies', views.FeedbackReplyViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
