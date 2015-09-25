import os

from django.contrib.auth import get_user_model
from django.utils.html import simple_email_re
from django.contrib import messages

from django.utils import timezone
from datetime import datetime

from . import defaults as defs


def get_user_by_username_or_email(username_or_email):
    """
    Returns a user given an email or username.
    """
    User = get_user_model()
    try:
        if simple_email_re.match(username_or_email):
            user = User.objects.get(email__iexact=username_or_email)
        else:
            user = User.objects.get(username__iexact=username_or_email)
    except User.DoesNotExist:
            return None
    return user


def get_template_path(name):
    """
    Given a template name, it returns the relative path from the template dir.
    """
    path = os.path.join(defs.USERWARE_TEMPLATE_BASE_DIR, name)
    return path


def has_pending_messages(request):
    """
    Given a request object it returns true if there are pending messages for session.
    """
    pending = len(messages.api.get_messages(request)) > 0
    return pending
