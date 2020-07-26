"""
This module registers URL patterns for the 'api' app.
"""

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

# Create the schema view
schema_view = get_schema_view(
    openapi.Info(
        title = "Focus API",
        default_version = "v1",
        contact = openapi.Contact(email="manipandey.shailesh@gmail.com"),
    ),
    public = True,
    permission_classes = (permissions.AllowAny,),
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),

    # Swagger URLs
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
]
