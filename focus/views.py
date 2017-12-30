"""
This modules container the views related to the Project in itself.
"""

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.views import LoginView
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer


class FacebookLogin(SocialLoginView):
    """
    View to enable login via Facebook using Oauth2.
    """
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(LoginView):
    """
    View to enable login via Twitter using Oauth.
    """
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter
