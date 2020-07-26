"""
This modules container the views related to authentication.
"""

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter

from rest_auth.views import LoginView
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def django_rest_auth_null():
    return Response(status = status.HTTP_400_BAD_REQUEST)


@api_view()
def email_verified(request):
    return Response(data = "Your have successfully verified your email! "
                         + "You can now log in to your account.",
                    status = status.HTTP_200_OK)


class FacebookLogin(SocialLoginView):
    """
    Login via Facebook using Oauth2.
    """
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(LoginView):
    """
    Login via Twitter using Oauth.
    """
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter
