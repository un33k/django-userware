from django.contrib.auth import get_user_model
from django.utils.html import simple_email_re

from django.utils import timezone
from datetime import datetime

User = get_user_model()


def get_user_by_username_or_email(username_or_email):
    """
    Returns a user given an email or username.
    """
    try:
        if simple_email_re.match(username_or_email):
            user = User.objects.get(email__iexact=username_or_email)
        else:
            user = User.objects.get(username__iexact=username_or_email)
    except User.DoesNotExist:
            return None
    return user
