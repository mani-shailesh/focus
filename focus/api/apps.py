"""
This module houses the Configuration class for django app.
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Class to represent configuration of an app
    """
    name = 'api'
