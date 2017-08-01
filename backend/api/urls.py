"""
This module registers URL patterns for the 'api' app.
"""

from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^clubs/$', views.ClubList.as_view()),
    url(r'^clubs/(?P<pk>[0-9]+)/$', views.ClubDetail.as_view()),
    url(r'^clubroles/$', views.ClubRoleList.as_view()),
    url(r'^clubroles/(?P<pk>[0-9]+)/$', views.ClubRoleDetail.as_view()),
    url(r'^clubmembers/$', views.ClubMembershipList.as_view()),
    url(r'^clubmembers/(?P<pk>[0-9]+)/$',
        views.ClubMembershipDetail.as_view()),
    url(r'^channels/$', views.ChannelList.as_view()),
    url(r'^channels/(?P<pk>[0-9]+)/$', views.ChannelDetail.as_view()),
    url(r'^posts/$', views.PostList.as_view()),
    url(r'^posts/(?P<pk>[0-9]+)/$', views.PostDetail.as_view()),
    url(r'^conversations/$', views.ConversationList.as_view()),
    url(r'^conversations/(?P<pk>[0-9]+)/$',
        views.ConversationDetail.as_view()),
    url(r'^projects/$', views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view()),
    url(r'^feedbacks/$', views.FeedbackList.as_view()),
    url(r'^feedbacks/(?P<pk>[0-9]+)/$', views.FeedbackDetail.as_view()),
    url(r'^feedbackreplies/$', views.FeedbackReplyCreate.as_view()),
    url(r'^feedbackreplies/(?P<pk>[0-9]+)/$',
        views.FeedbackReplyDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
