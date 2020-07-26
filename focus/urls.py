"""focus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from rest_framework_swagger.views import get_swagger_view
from django.contrib import admin
from .views import FacebookLogin, TwitterLogin

urlpatterns = [
    # Django auth urls
    url(r'^', include('django.contrib.auth.urls')),
    # Our api endpoints
    url(r'^api/', include('api.urls')),
    # Django admin endpoints
    url(r'^admin/', admin.site.urls),
    # Authorization related endpoints
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^auth/twitter/$', TwitterLogin.as_view(), name='twitter_login'),
    # Documentation related endpoints
    url(r'^docs/$', get_swagger_view(title='Focus API'))
]
