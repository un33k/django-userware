from .. import defaults as defs
from .. import utils as util


class UserSwitchMiddleware(object):
    """
    Middleware that handles the `su` functionality.
    """
    def process_request(self, request):
        if defs.USERWARE_SWTICHED_USER_KEY in request.session:
            username = request.session[defs.USERWARE_SWTICHED_USER_KEY]
            user = util.get_user_by_username_or_email(username)
            if user:
                request.user = user
