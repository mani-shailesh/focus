"""
This module contains the custom Adapter(s) needed for this app.
"""

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomDefaultAccountAdapter(DefaultAccountAdapter):
    """
    Default account adapter for custom URL in confirmation mail.
    """

    def send_mail(self, template_prefix, email, context):
        """
        Override this to inject our custom 'activate_url' in the context
        """
        context['activate_url'] = settings.EMAIL_CONFIRMATION_URL + context['key']
        msg = self.render_mail(template_prefix, email, context)
        msg.send()
