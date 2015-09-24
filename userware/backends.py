from django.contrib.auth.backends import ModelBackend as DjangoModelBackend

from . import utils as util


class ModelBackend(DjangoModelBackend):
    """ Authenticates user against username or email address"""

    def authenticate(self, username=None, password=None):
        """
        Handles if this is an email-based authentication.
        """
        user = util.get_user_by_username_or_email(username)
        if user and user.check_password(password):
            return user
        return None
