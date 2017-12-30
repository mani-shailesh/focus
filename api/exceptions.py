from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class ActionNotAvailable(APIException):
    """
    Exception to raise when an action on an instance is not available.
    """
    status_code = 422
    default_detail = _('Action "{action}" is not available.')
    default_code = 'action_unavailable'

    def __init__(self, action, detail=None, code=None):
        if detail is None:
            detail = force_text(self.default_detail).format(action=action)
        if code is None:
            code = self.default_code
        super(ActionNotAvailable, self).__init__(detail, code)
