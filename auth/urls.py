from django.conf.urls import include, url

from allauth.account.views import ConfirmEmailView

from rest_auth.views import LogoutView

from . import views

urlpatterns = [
    url(r'^registration/verification-email-sent/$',
            views.django_rest_auth_null,
            name='account_email_verification_sent'),
    url(r'^registration/verify-email/(?P<key>[-:\w]+)/$',
            ConfirmEmailView.as_view(),
            name='account_confirm_email'),
    url(r'^registration/email-verified/',
            views.email_verified),
    # TODO: Add a view to allow resending verification email
    url(r'^registration/resend-verification-email/$',
            views.django_rest_auth_null,
            name='account_email'),
    url(r'^registration/logout/$',
            LogoutView.as_view(),
            name='account_logout'),
    url(r'^', include('rest_auth.urls')),
    url(r'^registration/', include('rest_auth.registration.urls')),
    # Social media authorization endpoints
    url(r'^facebook/$', views.FacebookLogin.as_view(), name='fb_login'),
    url(r'^twitter/$', views.TwitterLogin.as_view(), name='twitter_login'),
]
